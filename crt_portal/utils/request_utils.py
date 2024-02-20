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


def add_nonce_to_html(html):
    current_request = CrequestMiddleware.get_request()
    nonce = str(current_request.csp_nonce)
    soup = BeautifulSoup(html, 'html.parser')

    scripts = soup.find_all('script')
    for script in scripts:
        script['nonce'] = nonce

    styles = soup.find_all('style')
    for style in styles:
        style['nonce'] = nonce

    return str(soup)
