"""
This is where to put views that need authentication.
 - CRT-only views should not be translated
 - Add a test to ensure authentication
 - Be mindful of any naming collision with public URLs in settings
"""
import contextlib
import io
import json
import logging
import mimetypes
import os
import urllib.parse

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation, BadRequest
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db.models import F, Subquery, OuterRef, Value, CharField, DateField, Case, When
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.html import mark_safe
from django.views.generic import FormView, TemplateView, View
from formtools.wizard.views import SessionWizardView
from analytics.models import AnalyticsFile, get_intake_notebooks
from tms.models import TMSEmail
from datetime import datetime
from django.db.models.functions import ExtractYear, Cast, Concat
from django.contrib.auth.models import Group

from .attachments import ALLOWED_FILE_EXTENSIONS
from .filters import report_filter, dashboard_filter, report_grouping
from .forms import (
    BatchReviewForm, BulkActionsForm, BulkDispositionForm, CommentActions, ComplaintActions, ComplaintOutreach,
    ContactEditForm, Filters, PrintActions, ProfileForm,
    ReportEditForm, ResponseActions, SavedSearchActions, SavedSearchFilter, add_activity,
    AttachmentActions, Review, save_form,
)
from .mail import mail_to_complainant
from .model_variables import BATCH_STATUS_CHOICES, HATE_CRIMES_TRAFFICKING_MODEL_CHOICES, NOTIFICATION_PREFERENCE_CHOICES
from .models import CommentAndSummary, Profile, Report, ReportAttachment, ReportDisposition, ReportDispositionBatch, ReportsData, RetentionSchedule, SavedSearch, Trends, EmailReportCount, Campaign, User, NotificationPreference, RoutingSection, RoutingStepOneContact, RepeatWriterInfo
from .page_through import pagination
from .sorts import other_sort, report_sort

logger = logging.getLogger(__name__)

SORT_DESC_CHAR = '-'


def format_protected_class(p_class_objects, other_class):
    p_class_list = []
    for p_class in p_class_objects:
        if p_class.value:
            code = p_class.code
            if code != 'Other':
                p_class_list.append(code)
            # If this code is other but there is no other_class description, we want it to say "Other". If there is an other_class that will take the place of "Other"
            elif other_class is None:
                p_class_list.append(code)

    return p_class_list


def get_section_contacts(purpose: str):
    routing_sections = RoutingSection.objects.all()
    try:
        routing_step_one_contacts = RoutingStepOneContact.objects.first().contacts
    except AttributeError:
        routing_step_one_contacts = "ask.CRT@usdoj.gov"
    routing_data = [
        {"section": route.section, "names": route.get_pocs(purpose)}
        for route in routing_sections
    ]

    return {"routing_data": routing_data, "routing_step_one_contacts": routing_step_one_contacts}


def reconstruct_query(next_qp):
    """
    Reconstruct the query filter on the previous page using the next
    query parameter. note that if next is empty, the resulting query
    will return all records.
    """
    querydict = QueryDict(next_qp)
    report_query, _ = report_filter(querydict)

    report_query = report_query.annotate(email_count=F('email_report_count__email_count'))

    sort_expr, sorts = report_sort(querydict.getlist('sort'))
    report_query = report_query.order_by(*sort_expr)

    return report_query


def preserve_filter_parameters(report, querydict):
    """
    Given a report and submission, preserve the `next` and `index`
    query parameters as these are essential to maintaining the current
    filter navigation.
    """
    return_url_args = querydict.get('next', '')
    next_page = urllib.parse.quote(return_url_args)
    index = querydict.get('index', '')

    if return_url_args:
        requested_ids = get_requested_ids(return_url_args)
        try:
            index = requested_ids.index(report.id)
        except ValueError:
            # rely on the index query param, if any. this will happen
            # if changes to the report cause the report to move out of
            # the filtered list.
            pass

    return f'{report.get_absolute_url()}?next={next_page}&index={index}'


def setup_filter_parameters(report, querydict):
    """
    If we have the `next` and `index` query parameters, then update
    the filter count, previous query, and next query so that filter
    navigation can continue apace.
    """
    output = {}
    return_url_args = querydict.get('next', '')
    index = querydict.get('index', None)

    if index == '':
        index = None

    if return_url_args and index is not None:
        requested_ids = get_requested_ids(return_url_args)

        index = int(index)
        if report.id in requested_ids:
            # override in case user input an invalid index
            index = requested_ids.index(report.id)
            output.update({
                'filter_current': index + 1,
            })
        else:
            # this report is no longer in the filter, but we want
            # to move backwards so that the previously next report
            # becomes the actual next report.
            index -= 1

        try:
            previous_id = requested_ids[index - 1] if index > 0 else None
            next_id = requested_ids[index + 1] if index < len(requested_ids) - 1 else None
            next_query = urllib.parse.quote(return_url_args)
        except IndexError:
            # When we cannot determine the next report page we are
            # removing the next button.
            return {}

        output.update({
            'filter_count': len(requested_ids),
            'filter_previous': previous_id,
            'filter_next': next_id,
            'filter_previous_query': f'?next={next_query}&index={index - 1}',
            'filter_next_query': f'?next={next_query}&index={index + 1}',
        })

    return output


def get_requested_ids(return_url_args):
    return_url_querydict = QueryDict(return_url_args[1:])
    activity = return_url_querydict.get('activity', None)
    if activity:
        requested_query = reconstruct_activity_query(return_url_args)
        return list(map(int, requested_query.values_list('target_object_id', flat=True)))
    requested_query = reconstruct_query(return_url_args)
    return list(requested_query.values_list('id', flat=True))


def reconstruct_activity_query(next_qp):
    """
    Reconstruct the query filter on the previous page using the next
    query parameter. note that if next is empty, the resulting query
    will return all records.
    """
    querydict = QueryDict(next_qp)

    _, selected_actions, _ = dashboard_filter(querydict)
    sort_expr, _ = other_sort(querydict.getlist('sort'), 'activity')
    if not selected_actions:
        return selected_actions
    return selected_actions.order_by(*sort_expr)


def reconstruct_id_args(ids):
    return ''.join([f'&id={id}' for id in ids])


def mark_report_as_viewed(report, user):
    if report.viewed:
        return
    now = datetime.now()
    description = f"Report viewed at {now.strftime('%m/%d/%y %H:%M:%M %p')}"
    add_activity(user, "Report viewed:", description, report)
    report.viewed = True
    report.save()


def mark_reports_as_viewed(reports, user):
    for report in reports:
        mark_report_as_viewed(report, user)


def _format_date(date_string):
    if date_string:
        return datetime.strptime(date_string, '%Y-%m-%d')
    return ""


def _related_reports_count(report):
    email = report.contact_email.upper()
    repeat_writer = RepeatWriterInfo.objects.filter(email=email).first()
    if repeat_writer:
        return repeat_writer.count
    # If the email is not in the repeat_writer table, initialize to 1.
    else:
        return 1


def get_profile_form(request):
    # Check for Profile object, then add filter to request
    if not hasattr(request.user, 'profile'):
        return ProfileForm()
    if not request.user.profile.intake_filters:
        return ProfileForm()

    request.GET = request.GET.copy()
    global_section_filter = request.user.profile.intake_filters.split(',')

    # If assigned_section is NOT specified in request, use filter from profile
    if 'assigned_section' not in request.GET:
        request.GET.setlist('assigned_section', global_section_filter)

    data = {'intake_filters': request.GET.getlist('assigned_section')}
    return ProfileForm(data)


def get_disposition_report_data(requested_reports):
    data = []
    for report in requested_reports:
        if report.retention_schedule and report.closed_date:
            report.expiration_date = datetime(report.closed_date.year + report.retention_schedule.retention_years + 1, 1, 1).date()
        url = reverse('crt_forms:crt-forms-show', kwargs={'id': report.pk})
        data.append({
            "report": report,
            "url": url,
        })
    return data


@login_required
def index_view(request):
    grouping = request.GET.get('grouping', 'default')
    profile_form = get_profile_form(request)
    selected_assignee_id = fetch_selected_foreign_key(
        request,
        'assigned_to',
        lambda text: User.objects.filter(username=text).first()
    )

    selected_campaign_uuid = fetch_selected_foreign_key(
        request,
        'origination_utm_campaign',
        lambda text: Campaign.objects.filter(internal_name=text).first()
    )
    if grouping != 'default':
        return render_group_view(request, profile_form, selected_assignee_id, selected_campaign_uuid, grouping)
    return render_default_view(request, profile_form, selected_assignee_id, selected_campaign_uuid)


def render_group_view(request, profile_form, selected_assignee_id, selected_campaign_uuid, grouping):
    group_queries, filters = report_grouping(request)
    group_params = json.loads(request.GET.get('group_params', "[]").replace("'", '"'))
    group_view_data = []
    updated_group_queries = []
    for i, group_query in enumerate(group_queries):
        requested_reports = group_query['qs'].annotate(email_count=F('email_report_count__email_count'))
        # Make sure query either has results or is the "All other reports" query
        if len(requested_reports) > 0 or i == (len(group_queries) - 1):
            group_query['requested_reports'] = requested_reports
            updated_group_queries.append(group_query)
    for i, updated_group_query in enumerate(updated_group_queries):
        params = group_params[i] if 0 <= i < len(group_params) else {'sort': [], 'per_page': 15, 'page': 1}
        group_data = get_group_view_data(request, updated_group_query['requested_reports'], filters, grouping, params, updated_group_query['desc_id'])
        group_view_data.append({
            "desc": updated_group_query['desc'],
            "desc_id": updated_group_query['desc_id'],
            "data": group_data
        })
    # Reset group params if number of groups has changed
    updated_group_params = []
    if len(updated_group_queries) != len(group_params):
        for query in enumerate(updated_group_queries):
            updated_group_params.append({
                "sort": [],
                "per_page": 15,
                "page": 1,
            })
    else:
        updated_group_params = group_params
    final_data = group_view_data[-1]["data"]
    final_data['return_url_args'] = urllib.parse.quote(f"{final_data['page_args']}&group_params={updated_group_params}")
    final_data.update({
        'profile_form': profile_form,
        'selected_assignee_id': selected_assignee_id,
        'selected_origination_utm_campaign': selected_campaign_uuid,
        'group_params': updated_group_params,
        'groups': group_view_data
    })

    return render(request, 'forms/complaint_view/index/grouped_index.html', final_data)


def render_default_view(request, profile_form, selected_assignee_id, selected_campaign_uuid):
    report_query, query_filters = report_filter(request.GET)

    if 'public_id' in query_filters and Report.all_objects.filter(public_id__startswith=query_filters.get('public_id')[0], disposed=True).exists():
        public_id = query_filters.get('public_id')[0].split('-')[0]
        batch_id = ReportDisposition.objects.get(public_id__startswith=f'{public_id}-').batch_id
        messages.add_message(request,
                             messages.WARNING,
                             mark_safe(f'This report ({public_id}) has been disposed and can not longer be viewed or recovered. <a href="/form/disposition/batch/{batch_id}">Click here to view the disposal batch</a>.'))

    final_data = get_view_data(request, report_query, query_filters)
    final_data.update({
        'profile_form': profile_form,
        'selected_assignee_id': selected_assignee_id,
        'selected_origination_utm_campaign': selected_campaign_uuid
    })
    response = render(request, 'forms/complaint_view/index/index.html', final_data)
    response.set_cookie('complaint_view_per_page', final_data['per_page'])
    return response


def get_group_view_data(request, requested_reports, query_filters, grouping, group_params, desc_id):
    # Sort data based on request from params, default to `created_date` of complaint
    per_page = group_params['per_page']
    page = group_params['page']
    sort = group_params['sort']
    sort_expr, sorts = report_sort(sort)

    requested_reports = requested_reports.order_by(*sort_expr)

    paginator = Paginator(requested_reports, per_page)
    requested_reports, page_format = pagination(paginator, page, per_page)

    sort_state = {}
    # make sure the links for this page have the same paging, sorting, filtering etc.
    report_url_args = f'?per_page={per_page}&grouping={grouping}'
    page_args = f'?grouping={grouping}'
    # process filter query params
    filter_args = get_filter_args(query_filters)
    page_args += filter_args
    report_url_args += filter_args

    if desc_id != -1:
        desc_filter = f'&violation_summary=^#{desc_id}$'
        report_url_args += desc_filter
    # process sort query params
    sort_args, sort_state = get_sort_args(sorts, sort_state)

    report_url_args += sort_args
    all_report_url_args_encoded = urllib.parse.quote(f'{report_url_args}&page={page}')
    all_args_encoded = urllib.parse.quote(f'{page_args}')

    paginated_offset = page_format['page_range_start'] - 1
    data = get_report_data(requested_reports, all_report_url_args_encoded, paginated_offset)

    return {
        'form': Filters(request.GET),
        'data_dict': data,
        'grouping': grouping,
        'page_format': page_format,
        'page_args': page_args,
        'sort_state': sort_state,
        'filter_state': filter_args,
        'filters': query_filters,
        'return_url_args': all_args_encoded,
    }


def get_view_data(request, report_query, query_filters, disposition_status=None):
    requested_reports = report_query.annotate(email_count=F('email_report_count__email_count'))

    # Sort data based on request from params, default to `created_date` of complaint
    per_page = request.GET.get('per_page', request.COOKIES.get('complaint_view_per_page', 15))
    page = request.GET.get('page', 1)

    sort_state = {}
    # make sure the links for this page have the same paging, sorting, filtering etc.
    if disposition_status:
        sort_expr, sorts = other_sort(request.GET.getlist('sort'), 'disposition')
        page_args = f'?per_page={per_page}'
        filter_args = get_filter_args(query_filters)
        requested_reports = requested_reports.annotate(dispo_status=Case(
            When(report_disposition_status=None, then=F('status')),
            default=F('report_disposition_status'),
        ))
        if '&disposition_status=' not in filter_args:
            filter_args += f'disposition_status={disposition_status}'
    else:
        sort_expr, sorts = report_sort(request.GET.getlist('sort'))
        page_args = f'?per_page={per_page}&grouping=default'
        filter_args = get_filter_args(query_filters)

    requested_reports = requested_reports.order_by(*sort_expr)
    paginator = Paginator(requested_reports, per_page)
    requested_reports, page_format = pagination(paginator, page, per_page)
    page_args += filter_args

    # process sort query params
    sort_args, sort_state = get_sort_args(sorts, sort_state)

    page_args += sort_args

    all_args_encoded = urllib.parse.quote(f'{page_args}&page={page}')

    paginated_offset = page_format['page_range_start'] - 1
    data = get_report_data(requested_reports, all_args_encoded, paginated_offset)

    return {
        'form': Filters(request.GET),
        'data_dict': data,
        'grouping': 'default',
        'page_format': page_format,
        'page_args': page_args,
        'per_page': per_page,
        'sort_state': sort_state,
        'filter_state': filter_args,
        'filters': query_filters,
        'return_url_args': all_args_encoded,
    }


def get_sort_args(sorts, sort_state):
    sort_args = ''
    for sort_item in sorts:
        if sort_item[0] == SORT_DESC_CHAR:
            sort_state.update({sort_item[1::]: True})
        else:
            sort_state.update({sort_item: False})

        sort_args += f'&sort={sort_item}'
    return sort_args, sort_state


def get_filter_args(query_filters):
    filter_args = ''
    for query_item in query_filters.keys():
        arg = query_item
        for item in query_filters[query_item]:
            filter_args = filter_args + f'&{arg}={item}'
    return filter_args


def get_report_data(requested_reports, report_url_args, paginated_offset):
    data = []
    for index, report in enumerate(requested_reports):
        p_class_list = format_protected_class(
            report.protected_class.all().order_by('form_order'),
            report.other_class,
        )
        # If a user has an email, it is looked up in the table to see if they are a repeat writer and add the count to the report.
        if report.contact_email:
            report.related_reports_count = _related_reports_count(report)
        if report.retention_schedule and report.closed_date:
            report.expiration_date = datetime(report.closed_date.year + report.retention_schedule.retention_years + 1, 1, 1).date()
        if report.other_class:
            p_class_list.append(report.other_class)
        if len(p_class_list) > 3:
            p_class_list = p_class_list[:3]
            p_class_list[2] = f'{p_class_list[2]}...'

        data.append({
            "report": report,
            "report_protected_classes": p_class_list,
            "url": f'{report.id}?next={report_url_args}&index={paginated_offset + index}',
        })
    return data


def fetch_selected_foreign_key(request, field_name, query):
    param_text = request.GET.get(field_name, "")
    if param_text == '(none)':
        return '-1'
    selected = query(param_text)
    return selected.pk if selected else ''


def process_intake_filters(request):
    query_filters, selected_actions, response_actions = dashboard_filter(request.GET)

    reports = selected_actions.values('target_object_id').distinct()
    start_date = _format_date(request.GET.get("create_date_start", ""))
    end_date = _format_date(request.GET.get("create_date_end", ""))

    selected_actor = request.GET.get("assigned_to", "")
    selected_actor_object = User.objects.filter(username=selected_actor).first()
    selected_actor_id = selected_actor_object.pk if selected_actor_object else ''

    return {
        'form': Filters(request.GET),
        'selected_actor': selected_actor,
        'selected_actor_id': selected_actor_id,
        'date_range_start': start_date,
        'date_range_end': end_date,
        'activity_count': reports.count(),
        'response_count': response_actions.count(),
        'filters': query_filters,
    }


def get_action_data(requested_actions, report_url_args, paginated_offset):
    data = []
    for index, action in enumerate(requested_actions):
        data.append({
            "action": action.verb,
            "detail": action.description,
            "timestamp": action.timestamp,
            "reportid": action.target_object_id,
            "url": f'/form/view/{action.target_object_id}/?next={report_url_args}&index={paginated_offset + index}'
        })
    return data


def process_activity_filters(request):
    query_filters, selected_actions, _ = dashboard_filter(request.GET)
    per_page = request.GET.get('per_page', 15)
    page = request.GET.get('page', 1)
    sort_expr, sorts = other_sort(request.GET.getlist('sort'), 'activity')
    if selected_actions != []:
        selected_actions = selected_actions.order_by(*sort_expr)
    paginator = Paginator(selected_actions, per_page)
    selected_actions, page_format = pagination(paginator, page, per_page)
    sort_state = {}
    # make sure the links for this page have the same paging, sorting, filtering etc.
    page_args = f'?activity=true&per_page={per_page}'

    filter_args = get_filter_args(query_filters)
    page_args += filter_args

    sort_args, sort_state = get_sort_args(sorts, sort_state)

    page_args += sort_args
    all_args_encoded = urllib.parse.quote(f'{page_args}&page={page}')

    paginated_offset = page_format['page_range_start'] - 1
    selected_actor = request.GET.get("assigned_to", "")
    selected_actor_object = User.objects.filter(username=selected_actor).first()
    selected_actor_id = selected_actor_object.pk if selected_actor_object else ''
    data = get_action_data(selected_actions, all_args_encoded, paginated_offset)
    return {
        'form': Filters(request.GET),
        'selected_actor': selected_actor,
        'selected_actor_id': selected_actor_id,
        'filters': query_filters,
        'data': data,
        'page_format': page_format,
        'page_args': page_args,
        'sort_state': sort_state,
        'filter_state': filter_args,
        'filters': query_filters,
        'return_url_args': all_args_encoded,
    }


@login_required
def data_view(request):
    profile_form = get_profile_form(request)

    return render(
        request,
        'forms/complaint_view/data/index.html',
        {
            'profile_form': profile_form,
            'intake_notebooks': get_intake_notebooks(),
        })


@login_required
def data_piecemeal_view(request, notebook_names):
    notebook_paths = [
        f'assignments/intake-dashboard/{name.strip()}.ipynb'
        for name in notebook_names.split(',')
    ]

    notebooks = [
        get_object_or_404(AnalyticsFile, path=path)
        for path in notebook_paths
    ]

    html = [
        notebook.to_html()
        for notebook in notebooks
    ]

    return render(
        request,
        'forms/complaint_view/data/piecemeal.html',
        {
            'notebooks': html,
        },
    )


@login_required
def dashboard_view(request):
    return render(
        request,
        'forms/complaint_view/dashboard/index.html',
        {
            **process_intake_filters(request),
        })


@login_required
def dashboard_activity_log_view(request):

    return render(
        request,
        'forms/complaint_view/dashboard/activity-log.html',
        {
            **process_activity_filters(request),
        })


def serialize_data(report, request, report_id):
    crimes = {
        'physical_harm': False,
        'trafficking': False
    }

    # for archival data
    for crime in report.hatecrimes_trafficking.all():
        for choice in HATE_CRIMES_TRAFFICKING_MODEL_CHOICES:
            if crime.value == choice[0]:
                crimes[choice[0]] = True

    p_class_list = format_protected_class(
        report.protected_class.all().order_by('form_order'),
        report.other_class,
    )

    return_url_args = request.GET.get('next', '')
    return_url_args = urllib.parse.unquote(return_url_args)
    querydict = QueryDict(return_url_args).dict()
    activity = querydict.get('?activity', None)
    if activity:
        view_type = 'activity'
    else:
        disposition_status = querydict.get('disposition_status', None)
        view_type = 'disposition' if disposition_status else 'records'

    output = {
        'actions': ComplaintActions(instance=report, user=request.user),
        'outreach': ComplaintOutreach(instance=report),
        'responses': ResponseActions(instance=report),
        'attachment_actions': AttachmentActions(),
        'comments': CommentActions(),
        'print_options': PrintActions(),
        'activity_stream': report.target_actions.all().prefetch_related('actor'),
        'attachments': report.attachments.filter(active=True),
        'reports_data_files': ReportsData.objects.all(),
        'crimes': crimes,
        'data': report,
        'p_class_list': p_class_list,
        'return_url_args': request.GET.get('next', ''),
        'index': request.GET.get('index', ''),
        'summary': report.get_summary,
        # for print media consumption
        'print_actions': report.activity(),
        'questions': Review.question_text,
        'view_type': view_type,
    }

    return output


def get_section_args(section_filters):
    if not section_filters:
        return ''
    return ''.join([
        f'&section_filter={section_filter}'
        for section_filter in section_filters
        if section_filter != ""
    ])


def get_batch_data(disposition_batches, all_args_encoded):
    data = []
    for batch in disposition_batches:
        url = reverse('crt_forms:disposition-batch-actions', kwargs={'id': batch.uuid})
        data.append({
            'batch': batch,
            'truncated_uuid': f'...{str(batch.uuid)[-6:]}',
            'retention_schedule': RetentionSchedule.objects.get(pk=batch.retention_schedule).name if batch.retention_schedule else '',
            'url': f'{url}?return_url_args={all_args_encoded}',
        })
    return data


def get_batch_view_data(request):
    disposition_batches = ReportDispositionBatch.objects.all()
    status_filter = request.GET.get('status', request.COOKIES.get('disposition_view_batch_status', ''))
    if status_filter:
        disposition_batches = disposition_batches.filter(status=status_filter)
    per_page = request.GET.get('per_page', request.COOKIES.get('complaint_view_per_page', 15))
    page = request.GET.get('page', 1)
    sort_expr, sorts = other_sort(request.GET.getlist('sort'), 'batch')
    disposition_batches = disposition_batches.annotate(retention_schedule=Subquery(ReportDisposition.objects.filter(batch=OuterRef("pk")).values_list('schedule', flat=True).distinct()))
    disposition_batches = disposition_batches.annotate(all_rejected=Subquery(ReportDisposition.objects.filter(batch=OuterRef("pk")).order_by('rejected').values_list('rejected', flat=True)[:1]))
    disposition_batches = disposition_batches.order_by(*sort_expr)
    statuses = map(lambda choice: choice[1].lower(), BATCH_STATUS_CHOICES)
    paginator = Paginator(disposition_batches, per_page)
    disposition_batches, page_format = pagination(paginator, page, per_page)
    sort_state = {}
    page_args = f'?per_page={per_page}&page={page}'
    sort_args, sort_state = get_sort_args(sorts, sort_state)
    page_args += sort_args
    filter_args = '&disposition_status=batches'
    page_args += filter_args
    all_args_encoded = urllib.parse.quote(page_args)
    data = get_batch_data(disposition_batches, all_args_encoded)
    can_approve_disposition = request.user.has_perm('cts_forms.approve_disposition') if request.user else False
    return {
        'can_approve_disposition': can_approve_disposition,
        'disposition_status': 'batches',
        'page_format': page_format,
        'page_args': page_args,
        'per_page': per_page,
        'sort_state': sort_state,
        'filter_state': filter_args,
        'return_url_args': all_args_encoded,
        'data': data,
        'statuses': statuses,
        'status': status_filter,
    }


@login_required
def disposition_view(request):
    params = request.GET.copy()
    if not params.get('disposition_status'):
        params['disposition_status'] = 'past'
    disposition_status = params.get('disposition_status')
    profile_form = get_profile_form(request)
    if disposition_status == 'batches':
        final_data = get_batch_view_data(request)
        response = render(request, 'forms/complaint_view/disposition/index.html', final_data)
        response.set_cookie('disposition_view_batch_status', final_data.get('status'))
        return response
    if params.get('status'):
        params.pop('status')
    report_query, query_filters = report_filter(params)

    # Records without these values should _never_ show on the disposition page,
    # regardless of user-selected filters:
    report_query = report_query.filter(
        status='closed',
        retention_schedule__retention_years__gt=0,
    ).exclude(
        retention_schedule__is_retired=True,
        retention_schedule__isnull=True,
    )

    final_data = get_view_data(request, report_query, query_filters, disposition_status)
    can_approve_disposition = request.user.has_perm('cts_forms.approve_disposition') if request.user else False

    schedules = (
        RetentionSchedule.objects.all()
        .filter(retention_years__gt=0)
        .exclude(is_retired=True)
        .order_by('retention_years')
    )

    expirations = (
        report_query.annotate(
            retention_year=F('retention_schedule__retention_years'),
            expiration_year=F('retention_year') + ExtractYear('closed_date') + 1,
            expiration_date=Cast(Concat(F('expiration_year'), Value('-01-01'), output_field=CharField()), output_field=DateField())
        )
        .order_by()
        .values_list('expiration_date', flat=True)
        .distinct()
    )

    final_data.update({
        'profile_form': profile_form,
        'disposition_status': disposition_status,
        'can_approve_disposition': can_approve_disposition,
        'schedules': schedules,
        'expirations': expirations,
    })
    return render(request, 'forms/complaint_view/disposition/index.html', final_data)


@login_required
def unsubscribe_view(request):
    if not hasattr(request.user, 'notification_preference'):
        messages.add_message(request,
                             messages.ERROR,
                             mark_safe("You are not subscribed to notifications"))
        return redirect(reverse('crt_forms:crt-forms-notifications'))

    request.user.notification_preference.delete()
    messages.add_message(request,
                         messages.SUCCESS,
                         mark_safe("You have been unsubscribed from all portal notifications"))
    return redirect(reverse('crt_forms:crt-forms-notifications'))


@login_required
def notification_view(request):
    if request.method == 'GET':
        return _notification_get(request)
    return _notification_change(request)


@login_required
def test_site_view(request):
    environment = os.environ.get('ENV', 'UNDEFINED')
    if environment not in ['LOCAL', 'UNDEFINED', 'STAGE', 'DEVELOP']:
        return HttpResponse(status=416)
    if request.method != 'GET':
        return HttpResponse(status=405)

    command_name = request.GET.get('command', '')
    if not command_name:
        return HttpResponse(status=400)

    if command_name not in [
        'create_mock_reports',
        'reset_disposition',
        'force_disposition'
    ]:
        return HttpResponse(status=400)

    args = request.GET.getlist('arg')
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        call_command(command_name, *args)
    output = stdout.getvalue()
    error = stderr.getvalue()
    output_part = f"<p>Command output:</p><pre>{output}</pre>" if output else ''
    error_part = f"<p>Command error:</p><pre>{error}</pre>" if error else ''
    message = f"<p>Command <strong>{command_name}</strong> executed.</p> {output_part} {error_part}"
    messages.add_message(request,
                         messages.WARNING,
                         mark_safe(message))

    return redirect(request.GET.get('next', '/form/view'))


def _notification_get(request):
    if hasattr(request.user, 'notification_preference'):
        preferences = request.user.notification_preference
    else:
        preferences = NotificationPreference(user=request.user)
    search_ids = [int(k) for k in preferences.saved_searches.keys()]
    search_names = {
        str(pk): name
        for pk, name
        in SavedSearch.objects.filter(id__in=search_ids).values_list('id', 'name')
    }
    return render(request, 'forms/complaint_view/notifications/index.html', {
        'search_names': search_names,
        'preferences': preferences,
        'choices': NOTIFICATION_PREFERENCE_CHOICES,
    })


def _notification_change(request):
    preference = NotificationPreference.objects.get_or_create(user=request.user)[0]

    changes = request.POST
    changed = False
    for key in changes:
        if key == 'csrfmiddlewaretoken':
            continue

        if not hasattr(preference, key):
            raise BadRequest(f"Not a valid notification setting: {key}")

        value = changes.getlist(key)[0]
        if getattr(preference, key) == value:
            continue

        setattr(preference, key, value)
        changed = True

    if not changed:
        messages.add_message(request,
                             messages.WARNING,
                             mark_safe("No changes were made"))
        return redirect(reverse('crt_forms:crt-forms-notifications'))

    preference.save()
    messages.add_message(request,
                         messages.SUCCESS,
                         mark_safe("Your preferences have been saved"))
    return redirect(reverse('crt_forms:crt-forms-notifications'))


class ProfileView(LoginRequiredMixin, FormView):
    # Can be used for updating section filter for a profile
    form_class = ProfileForm

    def post(self, request):
        # Update or create Profile
        if hasattr(request.user, 'profile'):
            instance = request.user.profile
        else:
            instance = Profile()
            instance.user = request.user

        profile_form = ProfileForm(request.POST, instance=instance)
        if profile_form.is_valid() and profile_form.has_changed():
            # Save Data in database
            profile_form.save()
        # redirects back to /form/view but all filter params are not perserved.
        return redirect(reverse('crt_forms:crt-forms-index'))


class ResponseView(LoginRequiredMixin, View):
    """
    Allow intake specialists to print, copy, or email form response letters
    If we encounter _any_ exceptions in sending an email, log the error message and return.
    """
    MAIL_SERVICE = "govDelivery TMS"
    ACTIONS = {'send': 'Emailed',
               'copy': 'Copied',
               'print': 'Printed'}
    SEND_MAIL_ERROR = "There was a problem sending the requested email. No email was sent. We've logged this error and will review it as soon as possible."

    def post(self, request, id):
        report = get_object_or_404(Report, pk=id)
        form = ResponseActions(request.POST, instance=report)
        url = preserve_filter_parameters(report, request.POST)

        if not form.has_changed():
            return redirect(url)
        if not form.is_valid():
            logging.error({'message': f"Form validation error: {form.errors}"})
            messages.add_message(request,
                                 messages.ERROR,
                                 mark_safe(
                                     "Sorry, we weren't able to do that:"
                                     f"{form.errors}"
                                     "Please refresh and try again."),
                                 )
            return redirect(url)

        tab = form.cleaned_data['selected_tab']
        template_kind = {
            'response-template-default': 'templates_default',
            'response-template-referral': 'templates_referral',
        }[tab]
        template = form.cleaned_data[template_kind]
        button_type = request.POST['type']
        optionals = {
            key.replace('optionals_', ''): request.POST.getlist(key)
            for key in request.POST.keys()
            if key.startswith('optionals_')
        }
        if optionals:
            template.optionals = optionals

        if button_type == 'send':  # We're going to send an email!
            try:
                sent = mail_to_complainant(report, template, TMSEmail.MANUAL_EMAIL)
                if sent:
                    description = f"Email sent: '{template.title}' to {report.contact_email} via {self.MAIL_SERVICE}"
                else:
                    description = f"{report.contact_email} not in allowed domains, not attempting to deliver {template.title}."
            except Exception as e:  # catch *all* exceptions
                logger.warning({'message': f"Email failed to send: {e}", 'report': report.id})
                messages.add_message(request, messages.ERROR, self.SEND_MAIL_ERROR)
                return redirect(url)  # Return here, nothing to write in activity log
        else:
            action = self.ACTIONS[button_type]
            description = f"{action} '{template.title}' template"

        messages.add_message(request, messages.SUCCESS, description)
        add_activity(request.user, "Contacted complainant:", description, report)

        return redirect(url)


class PrintView(LoginRequiredMixin, View):

    def post(self, request, id=None):
        form = PrintActions(request.POST)

        return_url_args = request.POST.get('modal_next', '')
        print_all = request.POST.get('type', None) == 'print_all'
        batch_id = request.POST.get('batch_id', None)
        return_url = request.POST.get('return_url', 'crt_forms:crt-forms-index')
        if print_all:
            reports = reconstruct_query(return_url_args)
        else:
            ids = request.POST.get('ids', '').split(',') if not id else [id]
            reports = Report.objects.filter(id__in=ids)

        if form.is_valid():
            options = form.cleaned_data['options']
            all_options = ', '.join(options)
            description = f"Printed {all_options}"
            for report in reports:
                add_activity(request.user, "Printed report", description, report)
            count = min(reports.count(), 100)
            description += f" for {count} reports"
            messages.add_message(request, messages.SUCCESS, description)

        if id:
            url = preserve_filter_parameters(report, request.POST)
        else:
            url = reverse(return_url, kwargs={'id': batch_id}) if batch_id else reverse(return_url)
            url = f"{url}{return_url_args}"
        return redirect(url)


class ShowView(LoginRequiredMixin, View):
    forms = {
        form.CONTEXT_KEY: form
        for form in [ContactEditForm, ComplaintActions, ComplaintOutreach, ReportEditForm]
    }

    def get(self, request, id):
        if Report.all_objects.filter(pk=id, disposed=True).exists():
            batch = get_object_or_404(ReportDisposition, public_id__startswith=f'{id}-')
            messages.add_message(request,
                                 messages.WARNING,
                                 'This report has been disposed of as part of the following disposition batch and can no longer be viewed or recovered.')
            return redirect(f'/form/disposition/batch/{batch.batch_id}')

        report = get_object_or_404(Report.objects.prefetch_related('attachments'), pk=id)
        # If a user has an email, it is looked up in the table to see if they are a repeat writer and add the count to the report.
        if report.contact_email:
            report.related_reports_count = _related_reports_count(report)
        output = serialize_data(report, request, id)
        if not report.viewed:
            mark_report_as_viewed(report, request.user)
        contact_form = ContactEditForm(instance=report)
        details_form = ReportEditForm(instance=report)
        filter_output = setup_filter_parameters(report, request.GET)
        autoresponse_email = TMSEmail.objects.filter(report=report.id, purpose=TMSEmail.AUTO_EMAIL).order_by('created_at').first()
        output.update({
            'contact_form': contact_form,
            'details_form': details_form,
            'email_enabled': settings.EMAIL_ENABLED,
            'allowed_file_types': ALLOWED_FILE_EXTENSIONS,
            'autoresponse_email': autoresponse_email,
            **filter_output,
            'routing_guide_link':
                f'/form/view/{id}/routing-guide/?{request.META["QUERY_STRING"]}',
            'disposition_guide_link':
                f'/form/view/{id}/disposition-guide/?{request.META["QUERY_STRING"]}',
        })
        return render(request, 'forms/complaint_view/show/index.html', output)

    def get_form(self, request, report):
        form_type = request.POST.get('type')
        if not form_type:
            raise SuspiciousOperation("Invalid form data")
        return self.forms[form_type](request.POST, request.FILES, instance=report, user=request.user), form_type

    def post(self, request, id):
        """
        Multiple forms are provided on the page
        Accept only the submitted form and discard any other inbound changes
        """
        report = get_object_or_404(Report, pk=id)

        form, inbound_form_type = self.get_form(request, report)
        if not (form.is_valid() and form.has_changed()):
            output = serialize_data(report, request, id)
            filter_output = setup_filter_parameters(report, request.POST)
            output.update({inbound_form_type: form, **filter_output})

            try:
                fail_message = form.FAIL_MESSAGE
            except AttributeError:
                fail_message = 'No updates applied'

            if not form.is_valid():
                error_items = ''.join([
                    f'<li>Problem modifying {field if field != "__all__" else "report"}: {error}</li>'
                    for field, error
                    in form.errors.items()
                ])
                fail_message += f'<ul>{error_items}</ul>'

            messages.add_message(request,
                                 messages.ERROR,
                                 mark_safe(fail_message))

            # Provide new for those not submitted
            for form_type, form in self.forms.items():
                if form_type != inbound_form_type:
                    output.update({form_type: form(instance=report, user=request.user)})
            return render(request, 'forms/complaint_view/show/index.html', output)
        report = form.save(commit=False)

        # Reset Assignee and Status if assigned_section is changed
        if 'assigned_section' in form.changed_data:
            primary_statute = report.primary_statute
            report.reset_for_changed_section()
            if primary_statute:
                description = f'Updated from "{primary_statute}" to "None"'
                add_activity(request.user, "Primary classification:", description, report)

        # District and location are on different forms so handled here.
        # If the incident location changes, update the district.
        # District can be overwritten in the drop down.
        # If there was a location change but no new match for district, don't override.
        if 'district' not in form.changed_data:
            current_district = report.district
            assigned_district = report.assign_district()
            if assigned_district and current_district != assigned_district:
                report.district = assigned_district
                description = f'Updated from "{current_district}" to "{report.district}"'
                add_activity(request.user, "District:", description, report)

        report.save()
        if 'contact_email' in form.changed_data:
            EmailReportCount.refresh_view()
        form.update_activity_stream(request.user)
        messages.add_message(request, messages.SUCCESS, form.success_message())

        url = preserve_filter_parameters(report, request.POST)
        return redirect(url)


class RoutingGuideView(LoginRequiredMixin, View):

    def get(self, request, id):
        output = get_section_contacts('routing')
        output['redirect_path'] = f'/form/view/{id}/?{request.META["QUERY_STRING"]}'
        return render(request, 'forms/complaint_view/routing_guide.html', output)


class DispositionGuideView(LoginRequiredMixin, View):

    def get(self, request, id):
        output = get_section_contacts('retention')
        output['redirect_path'] = f'/form/view/{id}/?{request.META["QUERY_STRING"]}'
        return render(request, 'forms/complaint_view/disposition_guide.html', output)


class DispositionActionsView(LoginRequiredMixin, FormView):
    """ CRT view to update report disposition"""
    EMPTY_CHOICE = 'Multiple'

    def get_shared_report_values(self, record_query, keys):
        """
        Given a record query and a list of keys, determine if a key has a
        singular value within that query. Used to set initial fields
        for bulk update forms.
        """
        # make sure the queryset does not order by anything, otherwise
        # we will have difficulty getting distinct results.
        query = record_query.order_by()
        query = query.annotate(
            retention_year=F('retention_schedule__retention_years'),
            expiration_year=F('retention_year') + ExtractYear('closed_date') + 1,
            expiration_date=Cast(Concat(F('expiration_year'), Value('-01-01'), output_field=CharField()), output_field=DateField())
        )
        for key in keys:
            values = query.values_list(key, flat=True).distinct()
            if values.count() != 1:
                yield key, self.EMPTY_CHOICE
                continue
            if key == 'retention_schedule':
                yield key, RetentionSchedule.objects.get(pk=values[0]).name
                continue
            if key == 'expiration_date':
                yield key, values[0].strftime('%m/%d/%Y')
                continue
            yield key, values[0]

    def get_report_date_range(self, record_query):
        query = record_query.order_by()
        intake_date = query.values_list('create_date', flat=True).order_by('create_date').first().strftime('%m/%d/%Y')
        close_date = query.values_list('closed_date', flat=True).order_by('closed_date').last().strftime('%m/%d/%Y')
        return f'{intake_date} - {close_date}'

    def reconstruct_id_args(self, ids):
        return ''.join([f'&id={id}' for id in ids])

    def get(self, request, id=None):
        rejected_batch_uuid = request.GET.get('rejected_batch_uuid', None)
        if rejected_batch_uuid:
            batch = get_object_or_404(ReportDispositionBatch, pk=rejected_batch_uuid)
            report_dispo_objects = ReportDisposition.objects.filter(batch=batch).filter(rejected=False)
            report_public_ids = report_dispo_objects.values_list('public_id', flat=True)
            reports = Report.objects.filter(public_id__in=report_public_ids).order_by('pk')
            ids = list(map(str, reports.values_list('pk', flat=True)))
        else:
            ids = request.GET.getlist('id')
        return_url_args = request.GET.get('next', '')
        return_url_args = urllib.parse.unquote(return_url_args)
        query_string = return_url_args
        selected_all = request.GET.get('all', '') == 'all'
        uuid = request.GET.get('uuid', None)
        if selected_all:
            requested_query = reconstruct_query(query_string)
            selected_report_args = 'all=all'
        else:
            requested_query = Report.objects.filter(pk__in=ids)
            selected_report_args = reconstruct_id_args(ids)

        disposition_status = request.GET.get('disposition_status', 'past')
        _, query_filters = report_filter(QueryDict(query_string))
        filter_args = f'{get_filter_args(query_filters)}'
        shared_report_fields = {}
        keys = ['assigned_section', 'retention_schedule', 'status', 'expiration_date']
        for key, value in self.get_shared_report_values(requested_query, keys):
            if key == 'expiration_date' and value == '-01-01':
                continue
            shared_report_fields[key] = value
        shared_report_fields['date_range'] = self.get_report_date_range(requested_query)
        # Limit the count to 500 here because we have to display all the reports we're batching in a table
        requested_query = requested_query[:500]
        all_ids_count = requested_query.count()
        ids_count = len(ids)

        selected_all = selected_all and all_ids_count != ids_count

        if selected_all:
            ids_count = all_ids_count
        page = request.GET.get('page', 1)
        paginator = Paginator(requested_query, 15)
        requested_query, page_format = pagination(paginator, page, 15)
        data = get_disposition_report_data(requested_query)
        next_args = urllib.parse.quote(f'{filter_args}')

        if not uuid:
            batch = ReportDispositionBatch.objects.create()
            uuid = batch.uuid
        else:
            batch = get_object_or_404(ReportDispositionBatch, pk=id)
        bulk_disposition_form = BulkDispositionForm(user=request.user, instance=batch)
        display_name = f'{request.user.first_name} {request.user.last_name}' if request.user.first_name and request.user.last_name else request.user.username
        output = {
            'action': request.GET.get('action', ''),
            'rejected_batch_uuid': rejected_batch_uuid,
            'uuid': uuid,
            'display_name': display_name,
            'disposed_by': request.user.pk,
            'return_url_args': f'?{filter_args}',
            'selected_all': 'all' if selected_all else '',
            'ids': ','.join(ids),
            'show_warning': ids_count > 50,
            'all_ids_count': ids_count,
            'shared_report_fields': shared_report_fields,
            'data': data,
            'bulk_disposition_form': bulk_disposition_form,
            'query_string': query_string,
            'id': id,
            'page_format': page_format,
            'page_args': f'?next={next_args}&{selected_report_args}',
            'per_page': 15,
            'disposition_status': disposition_status,
            'print_ids': list(map(int, ids)),
            'print_options': PrintActions(),
            'print_reports': requested_query,
        }
        return render(request, 'forms/complaint_view/disposition/actions/index.html', output)

    def post(self, request):
        return_url_args = request.POST.get('next', '')
        confirm_all = request.POST.get('confirm_all', '') == 'confirm_all'
        ids = request.POST.get('ids', '').split(',')
        selected_all = request.POST.get('all', '') == 'all'
        query_string = request.POST.get('query_string', return_url_args)
        rejected_batch_uuid = request.POST.get('rejected_batch_uuid')
        uuid = request.POST.get('uuid', None)
        if confirm_all:
            requested_query = reconstruct_query(query_string)
            requested_query.count() > 500
            selected_report_args = 'all=all'
        else:
            requested_query = Report.objects.filter(pk__in=ids)
            selected_report_args = reconstruct_id_args(ids)

        if not uuid:
            batch = ReportDispositionBatch.objects.create()
        else:
            batch = get_object_or_404(ReportDispositionBatch, pk=uuid)
        bulk_disposition_form = BulkDispositionForm(request.POST, user=request.user, instance=batch)
        if bulk_disposition_form.is_valid():
            if rejected_batch_uuid != 'None':
                rejected_batch = get_object_or_404(ReportDispositionBatch, pk=rejected_batch_uuid)
                rejected_batch.status = 'archived'
                rejected_batch.save()
            batch = bulk_disposition_form.save(commit=False)
            batch.save()
            bulk_disposition_form.update_reports(requested_query, request.user, batch)
            plural = 's have' if batch.disposed_count > 1 else ' has'
            message = f'{batch.disposed_count} record{plural} been approved for disposal. The records unit will review your request and approve or deny your deletion request. Follow status updates in ‘Report batches for disposal’'
            messages.add_message(request, messages.SUCCESS, message)
            # log this action for an audit trail.
            logger.info(f'Batch #{batch.uuid} with {batch.disposed_count} record{plural} has been created by {request.user}')
            url = reverse('crt_forms:disposition')
            return redirect(f"{url}{return_url_args}")
        else:
            for key in bulk_disposition_form.errors:
                errors = '; '.join(bulk_disposition_form.errors[key])
                if key == '__all__':
                    target = ':'
                else:
                    target = f' {key}:'
                error_message = f'Could not batch reports{target} {errors}'
                messages.add_message(request, messages.ERROR, error_message)
            _, query_filters = report_filter(QueryDict(query_string))

            disposition_status = request.GET.get('disposition_status', 'past')
            _, query_filters = report_filter(QueryDict(query_string))
            filter_args = f'{get_filter_args(query_filters)}'
            shared_report_fields = {}
            shared_report_fields['date_range'] = self.get_report_date_range(requested_query)
            keys = ['assigned_section', 'retention_schedule', 'expiration_date']
            for key, value in self.get_shared_report_values(requested_query, keys):
                shared_report_fields[key] = value
            shared_report_fields['date_range'] = self.get_report_date_range(requested_query)
            requested_query.count() > 500
            all_ids_count = requested_query.count()
            ids_count = len(ids)

            selected_all = selected_all and all_ids_count != ids_count
            if selected_all:
                ids_count = all_ids_count
            page = request.GET.get('page', 1)
            paginator = Paginator(requested_query, 15)
            requested_query, page_format = pagination(paginator, page, 15)
            data = get_disposition_report_data(requested_query)
            next_args = urllib.parse.quote(f'{filter_args}')
            display_name = f'{request.user.first_name} {request.user.last_name}' if request.user.first_name and request.user.last_name else request.user.username
            output = {
                'action': request.GET.get('action', ''),
                'uuid': batch.uuid,
                'display_name': display_name,
                'disposed_by': request.user.pk,
                'return_url_args': f'?{filter_args}',
                'selected_all': 'all' if selected_all else '',
                'ids': ','.join(ids),
                'show_warning': ids_count > 50,
                'all_ids_count': ids_count,
                'shared_report_fields': shared_report_fields,
                'data': data,
                'bulk_disposition_form': bulk_disposition_form,
                'query_string': query_string,
                'id': id,
                'page_format': page_format,
                'page_args': f'?next={next_args}&{selected_report_args}',
                'per_page': 15,
                'disposition_status': disposition_status,
                'print_ids': list(map(int, ids)),
                'print_options': PrintActions(),
                'print_reports': requested_query,
            }
            return render(request, 'forms/complaint_view/disposition/actions/index.html', output)


class DispositionBatchActionsView(LoginRequiredMixin, FormView):
    """ Records team view to review disposition batches"""

    def get_reviewer_data(self, request, batch):
        first_reviewer = batch.first_reviewer if batch.first_reviewer else request.user
        first_display_name = f'{first_reviewer.first_name} {first_reviewer.last_name}' if first_reviewer.first_name and first_reviewer.last_name else first_reviewer.username
        if batch.first_reviewer:
            second_reviewer = batch.second_reviewer if batch.second_reviewer else request.user
            second_display_name = f'{second_reviewer.first_name} {second_reviewer.last_name}' if second_reviewer.first_name and second_reviewer.last_name else second_reviewer.username
            second_reviewer_pk = second_reviewer.pk
        else:
            second_reviewer_pk = None
            second_display_name = None
        return {
            'first_reviewer': first_reviewer.pk,
            'first_display_name': first_display_name,
            'second_reviewer': second_reviewer_pk,
            'second_display_name': second_display_name,
        }

    def get(self, request, id=None):
        batch = get_object_or_404(ReportDispositionBatch, pk=id)
        report_dispo_objects = ReportDisposition.objects.filter(batch=batch)
        report_public_ids = report_dispo_objects.values_list('public_id', flat=True)
        reports = Report.objects.filter(public_id__in=report_public_ids).order_by('pk')
        report_ids = list(reports.values_list('pk', flat=True))
        first_report = reports.first()
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 15)
        reports, page_format = pagination(paginator, page, 15)
        return_url_args = request.GET.get('return_url_args', '')
        return_url_args = urllib.parse.unquote(return_url_args)
        shared_report_fields = {}
        shared_report_fields['assigned_section'] = first_report.assigned_section
        shared_report_fields['status'] = first_report.status
        shared_report_fields['retention_schedule'] = first_report.retention_schedule
        can_review_batch = request.user.has_perm('cts_forms.review_dispositionbatch')
        form = BatchReviewForm(user=request.user, can_review_batch=can_review_batch, instance=batch)
        data = get_disposition_report_data(reports)
        output = self.get_reviewer_data(request, batch)
        output.update({
            'batch': batch,
            'shared_report_fields': shared_report_fields,
            'data': data,
            'return_url_args': return_url_args,
            'page_format': page_format,
            'page_args': f'?return_url_args={urllib.parse.quote(return_url_args)}',
            'per_page': 15,
            'form': form,
            'ids': ','.join([str(id) for id in report_ids]),
            'ids_count': len(report_ids),
            'print_ids': list(map(int, report_ids)),
            'print_options': PrintActions(),
            'print_reports': reports,
            'truncated_uuid': f'...{str(batch.uuid)[-6:]}',
            'can_review_batch': can_review_batch,
        })
        return render(request, 'forms/complaint_view/disposition/actions/batch/index.html', output)

    def post(self, request, id=None):
        batch = get_object_or_404(ReportDispositionBatch, pk=id)
        can_review_batch = request.user.has_perm('cts_forms.review_dispositionbatch')
        form = BatchReviewForm(request.POST, user=request.user, can_review_batch=can_review_batch, instance=batch)
        return_url_args = request.POST.get('return_url_args', '')
        return_url_args = urllib.parse.unquote(return_url_args)
        if form.is_valid():
            rejected_report_ids = request.POST.get('rejected_report_ids', '').split(',')
            rejected_report_dispo_objects = ReportDisposition.objects.filter(public_id__in=rejected_report_ids)
            for report_dispo_object in rejected_report_dispo_objects:
                report = Report.objects.filter(public_id=report_dispo_object.public_id).first()
                report.batched_for_disposal = False
                report.report_disposition_status = 'rejected'
                report.save()
                report_dispo_object.rejected = True
                report_dispo_object.save()
            batch = form.save(commit=False)
            batch.save()
            if batch.status in ['approved', 'verified']:
                message = f'Batch #{batch.uuid} has been {batch.status} for disposal.'
                messages.add_message(request, messages.SUCCESS, message)
            elif batch.status == 'rejected':
                message = f'Batch #{batch.uuid} has been rejected for disposal.'
                messages.add_message(request, messages.ERROR, message)
            # log this action for an audit trail.
            logger.info(f'Batch #{batch.uuid} has been {batch.status} by {request.user}')
            url = reverse('crt_forms:disposition')
            return redirect(f"{url}{return_url_args}")
        for key in form.errors:
            errors = '; '.join(form.errors[key])
            if key == '__all__':
                target = ':'
            else:
                target = f' {key}:'
            error_message = f'Could not review batch{target} {errors}'
            messages.add_message(request, messages.ERROR, error_message)
        report_dispo_objects = ReportDisposition.objects.filter(batch=batch)
        report_public_ids = report_dispo_objects.values_list('public_id', flat=True)
        reports = Report.objects.filter(public_id__in=report_public_ids).order_by('create_date')
        report_ids = list(reports.values_list('pk', flat=True))
        first_report = reports.first()
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 15)
        reports, page_format = pagination(paginator, page, 15)
        data = get_disposition_report_data(reports)
        shared_report_fields = {}
        shared_report_fields['assigned_section'] = first_report.assigned_section
        shared_report_fields['status'] = first_report.status
        shared_report_fields['retention_schedule'] = first_report.retention_schedule
        output = self.get_reviewer_data(request, batch)
        output.update({
            'batch': batch,
            'shared_report_fields': shared_report_fields,
            'data': data,
            'return_url_args': return_url_args,
            'page_format': page_format,
            'page_args': f'?return_url_args={urllib.parse.quote(return_url_args)}',
            'per_page': 15,
            'form': form,
            'ids': ','.join([str(id) for id in report_ids]),
            'ids_count': len(report_ids),
            'print_ids': list(map(int, report_ids)),
            'print_options': PrintActions(),
            'print_reports': reports,
            'truncated_uuid': f'...{str(batch.uuid)[-6:]}',
            'can_review_batch': can_review_batch,
        })
        return render(request, 'forms/complaint_view/disposition/actions/batch/index.html', output)


class ActionsView(LoginRequiredMixin, FormView):
    """ CRT view to update report data"""

    def get(self, request):
        return_url_args = request.GET.get('next', '')
        return_url_args = urllib.parse.unquote(return_url_args)
        query_string = return_url_args
        group_desc_id = request.GET.get('group-desc-id', -1)
        if group_desc_id != -1:
            query_string = f'{return_url_args}&violation_summary=^#{group_desc_id}$'
        ids = request.GET.getlist('id')
        # The select all option only applies if 1. user hits the
        # select all button and 2. we have more records in the query
        # than the ids passed in
        selected_all = request.GET.get('all', '') == 'all'

        if selected_all:
            requested_query = reconstruct_query(query_string)
        else:
            requested_query = Report.objects.filter(pk__in=ids)

        bulk_actions_form = BulkActionsForm(requested_query, user=request.user)
        all_ids_count = requested_query.count()
        ids_count = len(ids)

        # further refine selected_all to ensure < 15 items don't show up.
        selected_all = selected_all and all_ids_count != ids_count

        output = {
            'action': request.GET.get('action', ''),
            'return_url_args': return_url_args,
            'selected_all': 'all' if selected_all else '',
            'ids': ','.join(ids),
            'ids_count': ids_count,
            'show_warning': ids_count > 15,
            'all_ids_count': all_ids_count,
            'bulk_actions_form': bulk_actions_form,
            'print_ids': list(map(int, ids)),
            'print_reports': requested_query,
            'print_options': PrintActions(),
            'questions': Review.question_text,
            'query_string': query_string,
        }
        return render(request, 'forms/complaint_view/actions/index.html', output)

    def post(self, request):
        return_url_args = request.POST.get('next', '')
        selected_all = request.POST.get('all', '') == 'all'
        confirm_all = request.POST.get('confirm_all', '') == 'confirm_all'
        ids = request.POST.get('ids', '').split(',')
        query_string = request.POST.get('query_string', return_url_args)

        if confirm_all:
            requested_query = reconstruct_query(query_string)
        else:
            requested_query = Report.objects.filter(pk__in=ids)

        if requested_query.count() > 500:
            raise BadRequest

        bulk_actions_form = BulkActionsForm(requested_query, request.POST, user=request.user)

        if bulk_actions_form.is_valid():
            number = bulk_actions_form.update(requested_query, request.user)
            description = bulk_actions_form.get_update_description()
            plural = 's have' if number > 1 else ' has'
            message = f'{number} record{plural} been updated: {description}'
            logging.info(message)
            messages.add_message(request, messages.SUCCESS, message)

            # log this action for an audit trail.
            logger.info(f'Bulk updating {number} requests by {request.user}: {description}')

            url = reverse('crt_forms:crt-forms-index')
            return redirect(f"{url}{return_url_args}")

        else:
            for key in bulk_actions_form.errors:
                errors = '; '.join(bulk_actions_form.errors[key])
                if key == '__all__':
                    target = ':'
                else:
                    target = f' {key}:'
                error_message = f'Could not bulk update{target} {errors}'
                messages.add_message(request, messages.ERROR, error_message)

            all_ids_count = requested_query.count()
            ids_count = len(ids)

            # further refine selected_all to ensure < 15 items don't show up.
            selected_all = selected_all and all_ids_count != ids_count

            output = {
                'return_url_args': return_url_args,
                'selected_all': 'all' if selected_all else '',
                'ids': ','.join(ids),
                'ids_count': ids_count,
                'show_warning': ids_count > 15,
                'all_ids_count': all_ids_count,
                'bulk_actions_form': bulk_actions_form,
                'print_ids': list(map(int, ids)),
                'print_reports': requested_query,
                'print_options': PrintActions(),
                'questions': Review.question_text,
            }
            return render(request, 'forms/complaint_view/actions/index.html', output)


class SavedSearchView(LoginRequiredMixin, FormView):

    def get_page_args(self, request, filter_args, saved_searches):
        per_page = request.GET.get('per_page', request.COOKIES.get('complaint_view_per_page', 15))
        page = request.GET.get('page', 1)
        sort_expr, sorts = other_sort(request.GET.getlist('sort'), 'saved_search')
        saved_searches = saved_searches.order_by(*sort_expr)
        paginator = Paginator(saved_searches, per_page)
        saved_searches, page_format = pagination(paginator, page, per_page)
        for saved_search in saved_searches:
            _, query_filters = report_filter(QueryDict(saved_search.query))
            saved_search.filters = query_filters
        sort_state = {}
        page_args = f'?per_page={per_page}'
        page_args += filter_args
        sort_args, sort_state = get_sort_args(sorts, sort_state)
        page_args += sort_args
        return {
            'saved_searches': saved_searches,
            'page_format': page_format,
            'page_args': page_args,
            'sort_state': sort_state,
            'filter_state': filter_args,
            'per_page': per_page,
        }

    def get(self, request):
        section_filter = request.GET.getlist('section_filter', [])
        filters = {'section__in': section_filter, 'shared': True} if section_filter else {'shared': True}
        saved_searches = SavedSearch.objects.filter(**filters).all()
        section_args = get_section_args(section_filter)
        saved_search_view = request.GET.get('saved_search_view', 'all')
        if saved_search_view == 'my-saved-searches':
            saved_searches = SavedSearch.objects.filter(created_by=request.user.id)
        filter_args = f'&saved_search_view={saved_search_view}{section_args}'
        output = {
            'section_filter': section_args,
            'form': SavedSearchFilter(request.GET),
            'saved_search_view': saved_search_view,
            **self.get_page_args(request, filter_args, saved_searches)
        }
        return render(request, 'forms/complaint_view/saved_searches/index.html', output)

    def post(self, request):
        section_filter = request.GET.getlist('section_filter', [])
        filters = {'section__in': section_filter, 'shared': True} if section_filter else {'shared': True}
        saved_searches = SavedSearch.objects.filter(**filters).all()
        section_args = get_section_args(section_filter)
        saved_search_view = request.GET.get('saved_search_view', 'all')
        if saved_search_view == 'my-saved-searches':
            saved_searches = SavedSearch.objects.filter(created_by=request.user.id)
        filter_args = f'&saved_search_view={saved_search_view}{section_args}'
        output = {
            'section_filter': section_args,
            'form': SavedSearchFilter(request.GET),
            'saved_search_view': saved_search_view,
            **self.get_page_args(request, filter_args, saved_searches)
        }
        return render(request, 'forms/complaint_view/saved_searches/index.html', output)


class SavedSearchActionView(LoginRequiredMixin, View):

    form = SavedSearchActions

    def is_group_admin(self, user, group):

        if not hasattr(group.group_preferences, 'admins'):
            return False
        admins = group.group_preferences.admins.filter(username=user.username)
        if user in admins:
            return True
        return False

    def get_group_data(self, user, id):
        group_data = []
        group_notification_preference = 'none'
        for group in Group.objects.all():
            if not hasattr(group, 'group_preferences') or not self.is_group_admin(user, group):
                continue
            group_notification_preference = group.group_preferences.saved_searches.get(str(id), 'none')
            group_data.append({
                'group': group,
                'notification_preferences': group_notification_preference,
                'field_name': f'group_{group.id}_saved_search_{id}',
                'notification_choices': NOTIFICATION_PREFERENCE_CHOICES['group_saved_search'],
            })
        return group_data

    def get(self, request, id=None):
        """
        Get saved search to edit
        """
        query_filters = []
        if id:
            saved_search = get_object_or_404(SavedSearch, pk=id)
            _, query_filters = report_filter(QueryDict(saved_search.query))
        else:
            saved_search = SavedSearch()
        query = request.GET.get('query', None)
        if query:
            _, query_filters = report_filter(QueryDict(query))
            query = get_filter_args(query_filters)
        section_filter = request.GET.get('section_filter', '')
        saved_search_view = request.GET.get('saved_search_view', 'all')
        name = request.GET.get('name', None)
        group_data = self.get_group_data(request.user, saved_search.id)
        if hasattr(request.user, 'notification_preference'):
            notification_preferences = request.user.notification_preference
        else:
            notification_preferences = NotificationPreference(user=request.user)
        if name:
            saved_search_form = SavedSearchActions(request.GET, instance=saved_search, user=request.user, group_data=group_data, notification_preferences=notification_preferences)
        else:
            saved_search_form = SavedSearchActions(query=query, instance=saved_search, user=request.user, group_data=group_data, notification_preferences=notification_preferences)
        output = {
            'form': saved_search_form,
            'section_filter': section_filter,
            'saved_search_view': f'&saved_search_view={saved_search_view}',
            'filters': query_filters,
            'notification_choices': NOTIFICATION_PREFERENCE_CHOICES,
            'notification_preferences': notification_preferences,
            'group_data': group_data,
        }
        if id:
            return render(request, 'forms/complaint_view/saved_searches/actions/update.html', output)
        return render(request, 'forms/complaint_view/saved_searches/actions/new.html', output)

    def post(self, request, id=None):
        section_filter = request.POST.get('section_filter', '')
        saved_search_view = request.POST.get('saved_search_view', 'all')
        url = reverse('crt_forms:saved-searches')
        delete = request.POST.get('delete', False)
        if not id:
            saved_search = SavedSearch()
            saved_search.created_by = request.user
        else:
            saved_search = get_object_or_404(SavedSearch, pk=id)
        group_data = self.get_group_data(request.user, saved_search.id)
        if hasattr(request.user, 'notification_preference'):
            notification_preferences = request.user.notification_preference
        else:
            notification_preferences = NotificationPreference(user=request.user)
        form = SavedSearchActions(request.POST, instance=saved_search, user=request.user, group_data=group_data, notification_preferences=notification_preferences)
        if delete:
            saved_search.delete()
            messages.add_message(request, messages.SUCCESS, form.success_message(id, delete))
            return redirect(f"{url}?{section_filter}{saved_search_view}")

        if not (form.is_valid() and form.has_changed()):
            output = {
                'form': form,
                'section_filter': section_filter,
                'id': saved_search.pk,
                'saved_search_view': f'&saved_search_view={saved_search_view}',
            }

            try:
                fail_message = form.FAIL_MESSAGE
            except AttributeError:
                fail_message = 'No updates applied'

            if not form.is_valid():
                error_items = ''.join([
                    f'<li>Problem modifying {field if field != "__all__" else "saved search"}: {error}</li>'
                    for field, error
                    in form.errors.items()
                ])
                fail_message += f'<ul>{error_items}</ul>'

            messages.add_message(request,
                                 messages.ERROR,
                                 mark_safe(fail_message))
            if not id:
                return render(request, 'forms/complaint_view/saved_searches/actions/new.html', output)
            return render(request, 'forms/complaint_view/saved_searches/actions/update.html', output)
        saved_search = form.save()
        messages.add_message(request, messages.SUCCESS, form.success_message(id))
        url = reverse('crt_forms:saved-searches')
        return redirect(f"{url}?{section_filter}{saved_search_view}")


class ReportAttachmentView(LoginRequiredMixin, FormView):
    """Can be used for saving attachments for a report"""
    form_class = AttachmentActions
    http_method_names = ['get', 'post']

    def get(self, request, id, attachment_id):
        """
        Download a particular attachment for a report
        """

        attachment = get_object_or_404(ReportAttachment, pk=attachment_id)

        logger.info(f'User {request.user} downloading attachment {attachment.filename} for report {id}')

        if settings.ENABLE_LOCAL_ATTACHMENT_STORAGE:
            try:
                file = open(attachment.file.name, 'rb')
                mime_type, _ = mimetypes.guess_type(attachment.filename)
                response = HttpResponse(file, content_type=mime_type)
                response.headers['Content-Disposition'] = f'attachment;filename={attachment.filename}'
                return response

            except FileNotFoundError:
                raise Http404(f'File {attachment.filename} not found.')

        else:
            # Generate a presigned URL for the S3 object
            s3_client = boto3.client(
                service_name='s3',
                region_name=settings.PRIV_S3_REGION,
                aws_access_key_id=settings.PRIV_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.PRIV_S3_SECRET_ACCESS_KEY,
                endpoint_url=settings.PRIV_S3_ENDPOINT_URL,
                config=Config(signature_version='s3v4'))

            try:
                response = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.PRIV_S3_BUCKET,
                        'Key': attachment.file.name,
                        'ResponseContentDisposition': f'attachment;filename={attachment.filename}'
                    },
                    ExpiresIn=30,
                )

                return redirect(response)

            except ClientError as e:
                logging.error(e)
                raise Http404(f'File {attachment.filename} not found.')

    def post(self, request, report_id):
        report = get_object_or_404(Report, pk=report_id)

        attachment_form = self.form_class(request.POST, request.FILES)

        if attachment_form.is_valid() and attachment_form.has_changed():
            attachment = attachment_form.save(commit=False)
            attachment.user = request.user
            attachment.save()

            verb = 'Attached file: '

            messages.add_message(request, messages.SUCCESS, f'Successfully {verb[:-2].lower()}')
            attachment_form.update_activity_stream(request.user, verb, attachment)
        else:
            for key in attachment_form.errors:
                errors = '; '.join(attachment_form.errors[key])
                error_message = f'Could not save attachment: {errors}'
                messages.add_message(request, messages.ERROR, error_message)

        url = preserve_filter_parameters(report, request.POST)
        return redirect(url)


class ReportDataView(LoginRequiredMixin, FormView):
    """Can be used for saving report data for a report"""
    http_method_names = ['get']

    def get(self, request, report_data_id):
        """
        Download a particular attachment for a report
        """
        attachment = get_object_or_404(ReportsData, pk=report_data_id)

        logger.info(f'User {request.user} downloading report data')

        if settings.ENABLE_LOCAL_ATTACHMENT_STORAGE:
            try:
                file = open(attachment.file.name, 'rb')
                mime_type, _ = mimetypes.guess_type(attachment.filename)
                response = HttpResponse(file, content_type=mime_type)
                response.headers['Content-Disposition'] = f'attachment;filename={attachment.filename}'
                return response

            except FileNotFoundError:
                raise Http404(f'File {attachment.filename} not found.')

        else:
            # Generate a presigned URL for the S3 object
            s3_client = boto3.client(
                service_name='s3',
                region_name=settings.PRIV_S3_REGION,
                aws_access_key_id=settings.PRIV_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.PRIV_S3_SECRET_ACCESS_KEY,
                endpoint_url=settings.PRIV_S3_ENDPOINT_URL,
                config=Config(signature_version='s3v4'))

            try:
                response = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.PRIV_S3_BUCKET,
                        'Key': attachment.file.name,
                        'ResponseContentDisposition': f'attachment;filename={attachment.filename}'
                    },
                    ExpiresIn=30,
                )

                return redirect(response)

            except ClientError as e:
                logging.error(e)
                raise Http404(f'File {attachment.filename} not found.')


class DataExport(LoginRequiredMixin, TemplateView):

    def get(self, request):
        output = {
            'reports_data_files': ReportsData.objects.all(),
        }
        return render(request, 'forms/data_export.html', output)


class RemoveReportAttachmentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, attachment_id):

        attachment = get_object_or_404(ReportAttachment, pk=attachment_id)

        logger.info(f'User {request.user} removing attachment with id {attachment_id}')

        attachment.active = False
        attachment.save()

        add_activity(request.user, "Removed attachment: ", attachment.filename, attachment.report)

        messages.add_message(request, messages.SUCCESS, f'Successfully removed {attachment.filename}')

        url = preserve_filter_parameters(attachment.report, request.POST)
        return redirect(url)


class SaveCommentView(LoginRequiredMixin, FormView):
    """Can be used for saving comments or summaries for a report"""
    form_class = CommentActions

    def post(self, request, report_id):
        """Update or create inbound comment"""
        report = get_object_or_404(Report, pk=report_id)
        comment_id = request.POST.get('comment_id')
        if comment_id:
            instance = get_object_or_404(CommentAndSummary, id=comment_id)
        else:
            instance = None

        comment_form = CommentActions(request.POST, instance=instance)

        if comment_form.is_valid() and comment_form.has_changed():
            comment = comment_form.save()
            report.internal_comments.add(comment)
            verb = 'Updated comment: ' if instance else 'Added comment: '

            messages.add_message(request, messages.SUCCESS, f'Successfully {verb[:-2].lower()}.')
            comment_form.update_activity_stream(request.user, report, verb)

            url = preserve_filter_parameters(report, request.POST)
            return redirect(url)
        else:
            for key in comment_form.errors:
                errors = '; '.join(comment_form.errors[key])
                error_message = f'Could not save comment: {errors}'
                messages.add_message(request, messages.ERROR, error_message)

            output = serialize_data(report, request, report_id)
            filter_output = setup_filter_parameters(report, request.POST)
            contact_form = ContactEditForm(instance=report)
            details_form = ReportEditForm(instance=report)
            output.update({
                'contact_form': contact_form,
                'details_form': details_form,
                'return_url_args': request.POST.get('next', ''),
                'index': request.POST.get('index', ''),
                **filter_output,
            })

            return render(request, 'forms/complaint_view/show/index.html', output)


class ProFormView(LoginRequiredMixin, SessionWizardView):
    """This is the one-page internal form for CRT staff to input complaints"""

    def get_template_names(self):
        return 'forms/pro_template.html'

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        field_errors = list(map(lambda field: field.errors, context['form']))
        page_errors = [error for field in field_errors for error in field]

        # internal use only
        ordered_step_names = [
            'Intake',
            'Contact',
            'Service member',
            'Primary concern',
            'Incident location',
            'Personal characteristics',
            'Date',
            'Personal Description',
        ]
        attachment_data = self.request.POST.get('pro_form_attachment', None)
        attachments = None
        if attachment_data:
            attachment_ids = attachment_data.split(',')[:-1]
            attachments = list(map(lambda id: get_object_or_404(ReportAttachment, pk=int(id)), attachment_ids))
        context.update({
            'field_errors': field_errors,
            'page_errors': page_errors,
            'num_page_errors': len(list(page_errors)),
            'word_count_text': {
                'wordRemainingText': 'word remaining',
                'wordsRemainingText': ' words remaining',
                'wordLimitReachedText': ' word limit reached',
            },
            'ordered_step_names': ordered_step_names,
            'stage_link': True,
            'submit_button': True,
            'form_novalidate': True,
            'pro_form_attachments': attachments,
        })

        return context

    def done(self, form_list, form_dict, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        cleaned_data.pop('pro_form_attachment')
        data, report = save_form(cleaned_data)
        pro_form_attachments = self.request.POST.get('pro_form_attachment', []).split(',')[:-1]
        attachments = [
            get_object_or_404(ReportAttachment, pk=int(id))
            for id in pro_form_attachments
        ]
        for attachment in attachments:
            attachment.report = report
            attachment.user = self.request.user
            attachment.save()
        EmailReportCount.refresh_view()
        return redirect(reverse('crt_forms:crt-forms-show', kwargs={'id': report.pk}))


class TrendView(LoginRequiredMixin, TemplateView):
    """This shows word trending for incoming reports"""
    template_name = "forms/complaint_view/trends.html"

    def get_context_data(self, **kwargs):
        return {
            'this_week': Trends.objects.filter(record_type='this_week'),
            'last_week': Trends.objects.filter(record_type='last_week'),
            'four_weeks': Trends.objects.filter(record_type='four_weeks'),
            'year': Trends.objects.filter(record_type='year'),
        }


class SearchHelperView(LoginRequiredMixin, TemplateView):
    """This shows advanced help text for the full-text search"""

    def get(self, request):
        return_url_args = request.GET.get('next', '')
        return_url_args = urllib.parse.unquote(return_url_args)

        output = {
            'return_url_args': return_url_args,
        }
        return render(request, 'forms/complaint_view/search_help.html', output)
