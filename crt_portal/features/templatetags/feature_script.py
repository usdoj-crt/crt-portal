import json

from django import template
from django.utils.safestring import mark_safe
from newrelic.common.async_wrapper import textwrap

from ..models import Feature

register = template.Library()


@register.simple_tag
def feature_script(csp_nonce):
    all_features = Feature.objects.all()

    feature_json = json.dumps({
        f.camel_case(): f.is_enabled()
        for f in all_features
    }, separators=(',', ':'))

    feature_classes = json.dumps([
        f.name for f in all_features if f.is_enabled()
    ], separators=(',', ':'))

    script = textwrap.dedent(f"""
        <script nonce="{csp_nonce}">
            const ENABLED_FEATURES = {feature_json};
            document.documentElement.classList.add(...{feature_classes});
        </script>
    """)
    # This is safe because the inputs are from admins, and are restricted.
    return mark_safe(script)  # nosec
