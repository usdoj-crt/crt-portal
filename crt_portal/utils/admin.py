from django.contrib import admin


EXTRA_QUERY_PARAMS = [
    'admin-tour',
    'admin-tour-step',
]


class CrtModelAdmin(admin.ModelAdmin):
    def get_list_filter(self, *args, **kwargs):
        passthrough = tuple([
            _make_passthrough_filter(param)
            for param in EXTRA_QUERY_PARAMS
        ])
        return super().get_list_filter(*args, **kwargs) + passthrough


def _make_passthrough_filter(param):
    class PassThroughFilter(admin.SimpleListFilter):
        """Does nothing - useful for passing a query param to javascript."""
        title = ''
        parameter_name = param
        template = 'admin/hidden_filter.html'

        def lookups(self, request, model_admin):
            return (request.GET.get(self.parameter_name), ''),

        def queryset(self, request, queryset):
            return queryset

    return PassThroughFilter
