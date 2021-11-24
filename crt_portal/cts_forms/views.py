"""
This is where to put views that need authentication.
 - CRT-only views should not be translated
 - Add a test to ensure authentication
 - Be mindful of any naming collision with public URLs in settings
"""
import logging
import mimetypes
import urllib.parse

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.paginator import Paginator
from django.db.models import F
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import FormView, TemplateView, View
from formtools.wizard.views import SessionWizardView
from tms.models import TMSEmail
from datetime import datetime

from .attachments import ALLOWED_FILE_EXTENSIONS
from .filters import report_filter, dashboard_filter
from .forms import (
    BulkActionsForm, CommentActions, ComplaintActions,
    ContactEditForm, Filters, PrintActions, ProfileForm,
    ReportEditForm, ResponseActions, add_activity,
    AttachmentActions, Review, save_form,
)
from .mail import crt_send_mail
from .model_variables import HATE_CRIMES_TRAFFICKING_MODEL_CHOICES
from .models import CommentAndSummary, Profile, Report, ReportAttachment, Trends, EmailReportCount
from .page_through import pagination
from .sorts import report_sort

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


def reconstruct_query(next_qp):
    """
    Reconstruct the query filter on the previous page using the next
    query parameter. note that if next is empty, the resulting query
    will return all records.
    """
    querydict = QueryDict(next_qp)
    report_query, _ = report_filter(querydict)

    report_query = report_query.annotate(email_count=F('email_report_count__email_count'))

    sort_expr, sorts = report_sort(querydict)
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
        requested_query = reconstruct_query(return_url_args)
        requested_ids = list(requested_query.values_list('id', flat=True))
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
        requested_query = reconstruct_query(return_url_args)
        requested_ids = list(requested_query.values_list('id', flat=True))

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


def _format_date(date_string):
    if date_string:
        return datetime.strptime(date_string, '%Y-%m-%d')
    return ""


@login_required
def index_view(request):
    profile_form = ProfileForm()
    # Check for Profile object, then add filter to request
    if hasattr(request.user, 'profile') and request.user.profile.intake_filters:
        request.GET = request.GET.copy()
        global_section_filter = request.user.profile.intake_filters.split(',')

        # If assigned_section is NOT specified in request, use filter from profile
        if 'assigned_section' not in request.GET:
            request.GET.setlist('assigned_section', global_section_filter)

        data = {'intake_filters': request.GET.getlist('assigned_section')}
        profile_form = ProfileForm(data)

    report_query, query_filters = report_filter(request.GET)

    # Sort data based on request from params, default to `created_date` of complaint
    per_page = request.GET.get('per_page', 15)
    page = request.GET.get('page', 1)

    requested_reports = report_query.annotate(email_count=F('email_report_count__email_count'))

    sort_expr, sorts = report_sort(request.GET)
    requested_reports = requested_reports.order_by(*sort_expr)

    paginator = Paginator(requested_reports, per_page)
    requested_reports, page_format = pagination(paginator, page, per_page)

    sort_state = {}
    # make sure the links for this page have the same paging, sorting, filtering etc.
    page_args = f'?per_page={per_page}'

    # process filter query params
    filter_args = ''
    for query_item in query_filters.keys():
        arg = query_item
        for item in query_filters[query_item]:
            filter_args = filter_args + f'&{arg}={item}'
    page_args += filter_args

    # process sort query params
    sort_args = ''
    for sort_item in sorts:
        if sort_item[0] == SORT_DESC_CHAR:
            sort_state.update({sort_item[1::]: True})
        else:
            sort_state.update({sort_item: False})

        sort_args += f'&sort={sort_item}'
    page_args += sort_args

    all_args_encoded = urllib.parse.quote(f'{page_args}&page={page}')

    data = []

    paginated_offset = page_format['page_range_start'] - 1
    for index, report in enumerate(requested_reports):
        p_class_list = format_protected_class(
            report.protected_class.all().order_by('form_order'),
            report.other_class,
        )
        if report.other_class:
            p_class_list.append(report.other_class)
        if len(p_class_list) > 3:
            p_class_list = p_class_list[:3]
            p_class_list[2] = f'{p_class_list[2]}...'

        data.append({
            "report": report,
            "report_protected_classes": p_class_list,
            "url": f'{report.id}?next={all_args_encoded}&index={paginated_offset + index}',
        })

    final_data = {
        'form': Filters(request.GET),
        'profile_form': profile_form,
        'data_dict': data,
        'page_format': page_format,
        'page_args': page_args,
        'sort_state': sort_state,
        'filter_state': filter_args,
        'filters': query_filters,
        'return_url_args': all_args_encoded,
    }

    return render(request, 'forms/complaint_view/index/index.html', final_data)


@login_required
def dashboard_view(request):
    query_filters, selected_actions = dashboard_filter(request.GET)

    # process filter query params
    filter_args = ''
    for query_item in query_filters.keys():
        arg = query_item
        for item in query_filters[query_item]:
            filter_args = filter_args + f'&{arg}={item}'

    reports_set = set()
    for action in selected_actions:
        reports_set.add(action.target_object_id)
    start_date = _format_date(request.GET.get("create_date_start", ""))
    end_date = _format_date(request.GET.get("create_date_end", ""))

    final_data = {
        'form': Filters(request.GET),
        'selected_actor': request.GET.get("assigned_to", ""),
        'date_range_start': start_date,
        'date_range_end': end_date,
        'activity_count': len(reports_set),
        'filters': query_filters,
    }
    return render(request, 'forms/complaint_view/dashboard/index.html', final_data)


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

    output = {
        'actions': ComplaintActions(instance=report),
        'responses': ResponseActions(instance=report),
        'attachment_actions': AttachmentActions(),
        'comments': CommentActions(),
        'print_options': PrintActions(),
        'activity_stream': report.target_actions.all().prefetch_related('actor'),
        'attachments': report.attachments.filter(active=True),
        'crimes': crimes,
        'data': report,
        'p_class_list': p_class_list,
        'return_url_args': request.GET.get('next', ''),
        'index': request.GET.get('index', ''),
        'summary': report.get_summary,
        # for print media consumption
        'print_actions': report.activity(),
        'questions': Review.question_text,
    }

    return output


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

        if form.is_valid() and form.has_changed():

            template = form.cleaned_data['templates']
            button_type = request.POST['type']

            if button_type == 'send':  # We're going to send an email!
                try:
                    sent = crt_send_mail(report, template, TMSEmail.MANUAL_EMAIL)
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
            url = reverse('crt_forms:crt-forms-index')
            url = f"{url}{return_url_args}"
        return redirect(url)


class ShowView(LoginRequiredMixin, View):
    forms = {
        form.CONTEXT_KEY: form
        for form in [ContactEditForm, ComplaintActions, ReportEditForm]
    }

    def get(self, request, id):
        report = get_object_or_404(Report.objects.prefetch_related('attachments'), pk=id)
        output = serialize_data(report, request, id)
        if not report.opened:
            now = datetime.now()
            description = f"Report opened at {now.strftime('%m/%d/%y %H:%M:%M %p')}"
            add_activity(request.user, "Report opened:", description, report)
            report.opened = True
            report.save()
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
        })
        return render(request, 'forms/complaint_view/show/index.html', output)

    def get_form(self, request, report):
        form_type = request.POST.get('type')
        if not form_type:
            raise SuspiciousOperation("Invalid form data")
        return self.forms[form_type](request.POST, request.FILES, instance=report), form_type

    def post(self, request, id):
        """
        Multiple forms are provided on the page
        Accept only the submitted form and discard any other inbound changes
        """
        report = get_object_or_404(Report, pk=id)

        form, inbound_form_type = self.get_form(request, report)
        if form.is_valid() and form.has_changed():
            report = form.save(commit=False)

            # Reset Assignee and Status if assigned_section is changed
            if 'assigned_section' in form.changed_data:
                report.status_assignee_reset()

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
        else:
            output = serialize_data(report, request, id)
            filter_output = setup_filter_parameters(report, request.POST)
            output.update({inbound_form_type: form, **filter_output})

            try:
                fail_message = form.FAIL_MESSAGE
            except AttributeError:
                fail_message = 'No updates applied'
            messages.add_message(request, messages.ERROR, fail_message)

            # Provide new for those not submitted
            for form_type, form in self.forms.items():
                if form_type != inbound_form_type:
                    output.update({form_type: form(instance=report)})

            return render(request, 'forms/complaint_view/show/index.html', output)


class ActionsView(LoginRequiredMixin, FormView):
    """ CRT view to update report data"""
    def get(self, request):
        return_url_args = request.GET.get('next', '')
        return_url_args = urllib.parse.unquote(return_url_args)

        ids = request.GET.getlist('id')
        # The select all option only applies if 1. user hits the
        # select all button and 2. we have more records in the query
        # than the ids passed in
        selected_all = request.GET.get('all', '') == 'all'

        if selected_all:
            requested_query = reconstruct_query(return_url_args)
        else:
            requested_query = Report.objects.filter(pk__in=ids)

        bulk_actions_form = BulkActionsForm(requested_query)
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

    def post(self, request):
        return_url_args = request.POST.get('next', '')
        selected_all = request.POST.get('all', '') == 'all'
        confirm_all = request.POST.get('confirm_all', '') == 'confirm_all'
        ids = request.POST.get('ids', '').split(',')

        if confirm_all:
            requested_query = reconstruct_query(return_url_args)
        else:
            requested_query = Report.objects.filter(pk__in=ids)

        if requested_query.count() > 500:
            raise PermissionDenied

        bulk_actions_form = BulkActionsForm(requested_query, request.POST)

        if bulk_actions_form.is_valid():
            number = bulk_actions_form.update(requested_query, request.user)
            description = bulk_actions_form.get_update_description()
            plural = 's have' if number > 1 else ' has'
            message = f'{number} record{plural} been updated: {description}'
            messages.add_message(request, messages.SUCCESS, message)

            # log this action for an audit trail.
            logger.info(f'Bulk updating {number} requests by {request.user}: {description}')

            url = reverse('crt_forms:crt-forms-index')
            return redirect(f"{url}{return_url_args}")

        else:
            for key in bulk_actions_form.errors:
                errors = '; '.join(bulk_actions_form.errors[key])
                error_message = f'Could not bulk update {key}: {errors}'
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
                response['Content-Disposition'] = f'attachment;filename={attachment.filename}'
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
            'Summary',
        ]

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
        })

        return context

    def done(self, form_list, form_dict, **kwargs):
        data, report = save_form(self.get_all_cleaned_data())
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
