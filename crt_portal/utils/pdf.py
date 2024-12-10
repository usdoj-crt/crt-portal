from typing import Any

from collections.abc import Callable
import io
import logging
import os

from django.conf import settings
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.http import content_disposition_header
import markdown
import pypdf
import weasyprint
import zipfile

from cts_forms import model_variables, question_text
from cts_forms.models import Report, ReportDispositionBatch
from utils.markdown_extensions import CustomHTMLExtension
from tms.models import TMSEmail
from django.contrib.postgres.aggregates import ArrayAgg


class FailedToGeneratePDF(RuntimeError):
    pass


_LEFT_ALIGN = weasyprint.CSS(string="""
    center {
        text-align: left !important;
    }
""")


def convert_html_to_pdf(source_html: str, stylesheets=[], **write_options) -> io.BytesIO:
    stylesheets = stylesheets + [_LEFT_ALIGN]
    out = io.BytesIO()
    try:
        weasyprint.HTML(
            string=source_html,
            media_type='screen',
        ).write_pdf(
            target=out,
            stylesheets=stylesheets,
            **write_options,
        )
    except Exception as error:
        raise FailedToGeneratePDF(f'Could not convert HTML\n\n{source_html}\n\n to pdf: {error}') from error
    return out


def _render_markdown(content: str) -> str:
    md = markdown.markdown(content,
                           extensions=['extra', 'sane_lists', 'admonition', 'nl2br', CustomHTMLExtension()])
    body = md + '<link rel="stylesheet" href="{% static "css/compiled/template-preview.css" %}">'
    return render_to_string('email.html', {'content': body})


def _make_cover_page(email: TMSEmail) -> str:
    meta = {
        'TMS ID': email.tms_id,
        'Report ID': email.report.id,
        'Subject': email.subject,
        'Recipient': email.recipient,
        'Created at': email.created_at,
        'Completed at': email.completed_at,
        'Status': email.status,
        'Purpose': email.purpose,
        'Error message': email.error_message,
    }
    meta_template = '\n'.join([
        '|        | Message Details |',
        '|--------|--------|',
        *[f'| {key} | {value} |' for key, value in meta.items()],
    ])
    return _render_markdown(f"""
The following email message (with Granicus TMS id {email.tms_id}) was sent by the Civil Rights Division to {email.recipient} on {email.completed_at}:

{meta_template}
    """)


def convert_tms_to_pdf(email: TMSEmail) -> io.BytesIO:
    cover_page = _make_cover_page(email)

    header_style = weasyprint.CSS(string=f"""
     @page {{
         @top-right{{
             content: "TMS ID #{email.tms_id}";
         }}
     }}
    """)

    pdf = pypdf.PdfWriter()
    pdf.append(convert_html_to_pdf(cover_page, stylesheets=[header_style]))
    pdf.append(convert_html_to_pdf(email.sent_content, stylesheets=[header_style]))
    out = io.BytesIO()
    pdf.write(out)
    return out


def convert_disposed_to_pdf(batch: ReportDispositionBatch) -> io.BytesIO:
    raw_reports_by_schedule = (
        batch.disposed_reports
        .values('schedule__name')
        .order_by('schedule__name')
        .annotate(public_ids=ArrayAgg('public_id'))
    )
    reports_by_schedule = {
        schedule['schedule__name']: schedule['public_ids']
        for schedule in raw_reports_by_schedule
    }

    meta = {
        'Batch ID': str(batch.uuid),
        'Disposed by': batch.disposed_by.get_username(),
        'Date of destruction': batch.disposed_date,
        '# Disposed Reports': batch.disposed_reports.count(),
        **{
            f'Disposed Reports ({schedule})': ', '.join(public_ids)
            for schedule, public_ids in reports_by_schedule.items()
        },
    }

    meta_template = '\n'.join([
        '|        | Message Details |',
        '|--------|--------|',
        *[f'| {key} | {value} |' for key, value in meta.items()],
    ])

    page = _render_markdown(f"""
The following reports were disposed by the Civil Rights Division on {batch.disposed_date} as part of batch {batch.uuid}:

{meta_template}
    """)

    header_style = weasyprint.CSS(string=f"""
     @page {{
         @top-right{{
             content: "Disposition Batch {batch.uuid}";
         }}
     }}
    """)

    pdf = pypdf.PdfWriter()
    pdf.append(convert_html_to_pdf(page, stylesheets=[header_style]))
    out = io.BytesIO()
    pdf.write(out)
    return out


def convert_report_to_pdf(report: Report) -> io.BytesIO:
    """Exports a report as a pdf."""
    data = {
        'complainant_letter': None,
        'template': None,
        'referral_contact': None,
        'report': model_to_dict(report),
    }
    html = render_to_string('referral_info.html', data)
    return convert_html_to_pdf(html)


def build_intake_form_pdf() -> io.BytesIO:
    try:
        content = convert_html_to_pdf(
            render_to_string('printable_intake_form.html', {
                'variables': model_variables,
                'questions': question_text,
            }),
            stylesheets=[
                os.path.join(settings.BASE_DIR, 'cts_forms', 'templates', 'local_fonts.css'),
                os.path.join(settings.BASE_DIR, 'cts_forms', 'templates', 'printable_intake_form.css'),
            ],
            pdf_forms=True,
        )
    except FailedToGeneratePDF as error:
        logging.exception(error)
        return HttpResponse("We're sorry, but something went wrong retrieving this form.", status=500)

    filename = _("File a complaint").replace(" ", "_").lower() + ".pdf"
    return HttpResponse(content.getvalue(),
                        content_type="application/pdf",
                        headers={'Content-Disposition': content_disposition_header(as_attachment=False, filename=filename)})


def admin_export_pdf(queryset, *,
                     pdf_filename: Callable[[Any], str],
                     zip_filename: str,
                     converter: Callable[[Any], io.BytesIO]) -> HttpResponse:
    """Exports a queryset as a pdf."""
    buffer = io.BytesIO()
    archive = zipfile.ZipFile(buffer, "w")

    if queryset.count() == 1:
        try:
            content = convert_report_to_pdf(queryset.first())
            return HttpResponse(content.getvalue(), content_type="application/pdf")
        except FailedToGeneratePDF as error:
            logging.exception(error)
            return HttpResponse(f'{error}', status=500)

    errors = []
    for report in queryset:
        try:
            content = convert_report_to_pdf(report)
            archive.writestr(f'{report.public_id}.pdf', content.getvalue())
        except FailedToGeneratePDF as error:
            logging.exception(error)
            errors.append(f'{report.public_id}: {error}')
    if errors:
        archive.writestr("errors.txt", "\n".join(errors))
    archive.close()

    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="reports_export.zip"'

    return response
