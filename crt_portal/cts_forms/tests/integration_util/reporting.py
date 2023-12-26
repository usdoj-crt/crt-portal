import weasyprint
import tempfile
import pathlib


def capture_report(path_to_pdf):
    """Decorator that captures screenshots and aggregates them into a PDF.

    Example:
        @capture_report('example.pdf')
        def test_example(page, *, report):
            report.screenshot(page, caption='Example screenshot')
    """
    def wrapper(func):
        def decorator(page, *args, **kwargs):
            report = PdfReport(path_to_pdf)
            result = func(page, *args, report=report, **kwargs)
            report.save()
            return result
        return decorator
    return wrapper


class PdfReport:
    """Captures multiple screenshots over time and aggregates them into a PDF."""

    def __init__(self, path_to_pdf):
        self.path_to_pdf = f'e2e-screenshots/{path_to_pdf}'
        self.screenshots = []

    def screenshot(self, page, caption='', **kwargs):
        if page.evaluate('() => document.body.classList.contains("is-modal")'):
            target = next(
                modal
                for modal
                in page.locator('.modal-wrapper').all()
                if modal.is_visible()
            )
            kwargs.pop('full_page', None)
        else:
            target = page

        self.screenshots.append({
            'file': target.screenshot(**kwargs),
            'caption': caption,
        })

    def _prepare_screenshots_for_save(self):
        temp = tempfile.mkdtemp()
        for index, screenshot in enumerate(self.screenshots):
            path = f'{temp}/{index}.png'
            screenshot['path'] = path
            with open(path, 'wb') as f:
                f.write(screenshot['file'])

    def _screenshot_to_html(self, screenshot):
        path = screenshot['path']
        caption = screenshot['caption']
        if not caption.strip().startswith('<'):
            caption = f'<p>{caption}</p>'
        return f'''
            <div class="page">
                <img src="file://{path}" />
                <div class="caption">{caption}</div>
            </div>
        '''

    def save(self):
        self._prepare_screenshots_for_save()

        directory = pathlib.Path(self.path_to_pdf).parent
        directory.mkdir(parents=True, exist_ok=True)

        stylesheet = weasyprint.CSS(
            string='''
                @page {
                    size: letter;
                    margin: 0;
                }
                body {
                    margin: 0;
                    padding: 0;
                }
                div.page {
                    page: page;
                    page-break-after: always;
                    margin-top: 0.5in;
                    width: 8.5in;
                }
                div.page > * {
                    width: 7.5in;
                    margin-left: 0.5in;
                }
                img {
                    margin-bottom: 1em;
                    border: 1px solid black;
                    max-height: 9in;
                    object-fit: contain;
                }
            '''
        )

        weasyprint.HTML(
            string=''.join([
                self._screenshot_to_html(screenshot)
                for screenshot
                in self.screenshots
            ])
        ).write_pdf(self.path_to_pdf,
                    stylesheets=[stylesheet])
