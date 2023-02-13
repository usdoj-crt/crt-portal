from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
import json
import markdown

from cts_forms.mail import CustomHTMLExtension


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
        md = markdown.markdown(markdown_body, extensions=['nl2br', CustomHTMLExtension()])
        return render(request, 'email.html', {'content': md})
    else:
        return HttpResponse(markdown_body.replace('\n', '<br>'))
