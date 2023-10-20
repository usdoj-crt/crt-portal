import io

from django.forms.models import model_to_dict
from django.template.loader import render_to_string
import markdown
import pypdf
import weasyprint

from cts_forms.models import Report
from cts_forms.mail import CustomHTMLExtension
from tms.models import TMSEmail


class FailedToGeneratePDF(RuntimeError):
    pass


_LEFT_ALIGN = weasyprint.CSS(string="""
    center {
        text-align: left !important;
    }
""")


def convert_html_to_pdf(source_html: str, stylesheets=[]) -> io.BytesIO:
    stylesheets = stylesheets + [_LEFT_ALIGN]
    out = io.BytesIO()
    try:
        weasyprint.HTML(
            string=source_html,
            media_type='screen',
        ).write_pdf(
            target=out,
            stylesheets=stylesheets,
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

    pdf = pypdf.PdfMerger()
    pdf.append(convert_html_to_pdf(cover_page, stylesheets=[header_style]))
    pdf.append(convert_html_to_pdf(email.sent_content, stylesheets=[header_style]))
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
