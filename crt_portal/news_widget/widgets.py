from django import forms


class ArticleListWidget(forms.Textarea):
    """Admin widget for editing a news column's list of articles.

    The underlying value is still a JSON array of ``{date, title, link}``
    objects stored in a JSONField, and the rendered <textarea> remains the
    input that is actually submitted and saved. `news_column_admin.js`
    progressively enhances that textarea into a friendly add / remove /
    reorder editor (with a date picker per article), while a "Show raw JSON"
    toggle lets power users edit the JSON directly.
    """

    template_name = 'news_widget/article_list_widget.html'

    class Media:
        js = ('js/news_column_admin.js',)
        css = {'all': ('css/news_column_admin.css',)}
