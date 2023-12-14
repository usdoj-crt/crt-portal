import io
import traceback
import zipfile

from .models import AnalyticsFile, DashboardGroup, FileGroupAssignment
from utils.admin import CrtModelAdmin

from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import mark_safe, escape


def export_notebooks_as_zip(modeladmin, request, queryset):
    """Export a zip file containing all of the database's response templates."""
    del request, modeladmin  # unused
    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, "w")

    for notebook in queryset:
        filename = notebook.path
        zip_file.writestr(filename, notebook.content)

    zip_file.close()

    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="notebooks.zip"'

    return response


class NotebookAdmin(CrtModelAdmin):
    class Media:
        css = {
            'all': ('css/compiled/admin.css',)
        }
        js = (
            'vendor/js.cookie.min.js',
            'js/admin_notebook_actions.js',
        )

    actions = [export_notebooks_as_zip]

    list_display = ('pk', 'name', 'path', 'last_modified', 'from_command')
    readonly_fields = ('name', 'path', 'created', 'last_modified', 'last_run', 'results', 'from_command')
    exclude = ('content', 'mimetype', 'format', 'type')

    change_form_template = "admin/notebook_change_form.html"

    def get_queryset(self, *args, **kwargs):
        return AnalyticsFile.objects.filter(type='notebook').exclude(path__endswith='/.ipynb_checkpoints')

    def response_change(self, request, obj: AnalyticsFile):
        if "_refresh_notebook" in request.POST:
            obj.refresh()
            obj.save()
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    @admin.display(description='Results')
    def results(self, obj: AnalyticsFile):
        try:
            html = escape(obj.to_html())
            return mark_safe(f"""
                <iframe class="ipynb-results" srcdoc="{html}"></iframe>
            """)
        except Exception as error:
            trace = '<br/>'.join([
                escape(s)
                for s in traceback.format_exception(error)
            ])
            return mark_safe(f"""
                <p>Error rendering notebook:</p>
                <code>{trace}</code>
            """)


class Notebook(AnalyticsFile):
    class Meta:
        proxy = True


class DashboardGroupAdmin(CrtModelAdmin):
    list_display = ('header', 'order')


class FileGroupAssignmentAdmin(CrtModelAdmin):
    pass

    list_display = ('display_group', 'display_files')

    def display_files(self, obj):
        return "\n".join([str(obj.analytics_file)])

    def display_group(self, obj):
        return "\n".join([str(obj.dashboard_group)])


admin.site.register(Notebook, NotebookAdmin)
admin.site.register(DashboardGroup, DashboardGroupAdmin)
admin.site.register(FileGroupAssignment, FileGroupAssignmentAdmin)
