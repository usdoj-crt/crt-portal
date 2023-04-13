from collections import defaultdict
from ..models import Feature


def enabled_features(request):
    """Adds a dictionary to the template context for features are enabled.

    For example, if you have a feature, 'my-feature', that's enabled:
        - `{{ enabled_features.my_feature }}` will render "True"
        - `{% if enabled_features.my_feature %}foo{%endif%}` will render "foo"

    The dictionary will return None for nonexistant features, so:
        - `{% if enabled_features.nonexistant %}foo{%endif%}` will be blank with no error.
    """
    del request  # Unused here.
    return {
        'ENABLED_FEATURES': defaultdict(None, **{
            feature.snake_case(): feature.enabled
            for feature in
            Feature.objects.all()
        })
    }
