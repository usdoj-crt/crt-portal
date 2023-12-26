from django.contrib import admin

from utils.admin import CrtModelAdmin
from .models import Feature


class FeatureAdmin(CrtModelAdmin):
    list_display = ('pk', 'title_case', 'name', 'enabled')
    readonly_fields = ('title_case', 'python_variable', 'javascript_variable')
    filter_horizontal = ('users_when_disabled',)

    @admin.display(description='Feature Title')
    def title_case(self, obj):
        if not obj.pk:
            return 'Save to generate title'
        return obj.title_case()

    @admin.display(description='Python Variable')
    def python_variable(self, obj):
        if not obj.pk:
            return 'Save to generate python'
        return obj.snake_case()

    @admin.display(description='Javascript Variable')
    def javascript_variable(self, obj):
        if not obj.pk:
            return 'Save to generate javascript'
        return obj.camel_case()


admin.site.register(Feature, FeatureAdmin)
