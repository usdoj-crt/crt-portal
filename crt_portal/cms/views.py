from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
import json
from django.template import Context, Template
import markdown

from cts_forms.mail import CustomHTMLExtension


BASE_CONTEXT = {
    'addressee': '[Variable: Addressee Name]',
    'contact_address_line_1': '[Variable: Contact Address Line 1]',
    'contact_address_line_2': '[Variable: Contact Address Line 2]',
    'contact_email': '[Variable: Contact Email]',
    'date_of_intake': '[Variable: Date of Intake]',
    'outgoing_date': '[Variable: Outgoing Date]',
    'section_name': '[Variable: Section]',
}

LANG_CONTEXTS = {
    lang: {
        key: f'[{lang}] {value}'
        for key, value in BASE_CONTEXT.items()
    } for lang in ['es', 'ko', 'tl', 'vi', 'zh_hans', 'zh_hant']
}

EXAMPLE_CONTEXT = Context({
    'record_locator': '[Variable: Record Locator]',
    **BASE_CONTEXT,
    **LANG_CONTEXTS,
})


@login_required
def index_view(request):
    return render(request, 'netlify.html')


@login_required
def config_view(request):
    response = render(request, 'netlify.yml')
    response['Content-Type'] = 'text/yaml'
    return response


@login_required
def render_email(request):
    raw = json.loads(request.body)
    entry = raw.get('entry', {})
    data = entry.get('data', {})
    markdown_body = data.get('body', '')

    if data.get('is_html', False):
        subbed = str(Template(markdown_body).render(EXAMPLE_CONTEXT))
        md = markdown.markdown(subbed, extensions=['nl2br', CustomHTMLExtension()])
        return render(request, 'email.html', {'content': md})

    return HttpResponse(Template(markdown_body.replace('\n', '<br>')).render(EXAMPLE_CONTEXT))
