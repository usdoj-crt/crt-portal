from crequest.middleware import CrequestMiddleware
from bs4 import BeautifulSoup


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_section():
    current_request = CrequestMiddleware.get_request()
    user = current_request.user
    if hasattr(user, 'profile'):
        return current_request.user.profile.section
    return None


def fix_mathjax(html):
    """To avoid requirement of unsafe eval.

    See: https://github.com/mathjax/MathJax/issues/1988#issuecomment-384978927
    """
    soup = BeautifulSoup(html, 'html.parser')

    scripts = soup.find_all('script', attrs={'type': 'text/x-mathjax-config'})
    for script in scripts:
        script.clear()

    return str(soup)


def add_nonce_to_html(html):
    current_request = CrequestMiddleware.get_request()
    if not current_request or not hasattr(current_request, 'csp_nonce'):
        return html
    nonce = str(current_request.csp_nonce)
    soup = BeautifulSoup(html, 'html.parser')

    scripts = soup.find_all('script')
    for script in scripts:
        script['nonce'] = nonce

    styles = soup.find_all('style')
    for style in styles:
        style['nonce'] = nonce

    return str(soup)
