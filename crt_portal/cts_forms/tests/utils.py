import bs4


def assertSoupFinds(response, *find_args, **find_kwargs):
    soup = bs4.BeautifulSoup(str(response.content), 'html.parser')
    body = soup.find('body')
    element = soup.find(*find_args, **find_kwargs)
    assert element is not None, f'Element not found: {find_kwargs} in {body}'


def assertSoupSelects(response, *select_args, **select_kwargs):
    soup = bs4.BeautifulSoup(str(response.content), 'html.parser')
    body = soup.find('body')
    element = soup.select_one(*select_args, **select_kwargs)
    assert element, f'Element not found: {select_kwargs} in {body}'
