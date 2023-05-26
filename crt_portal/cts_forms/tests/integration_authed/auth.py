def login_as_superuser(page):
    with page.expect_navigation():
        page.goto("/admin/logout")

    page.goto("/admin/login/?next=/admin/")

    try:
        with open('test-user-username.txt', 'r') as f:
            username = f.readline()
        with open('test-user-password.txt', 'r') as f:
            password = f.readline()
    except FileNotFoundError:
        raise RuntimeError('Please run manage.py create_test_user first.')

    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)

    with page.expect_navigation():
        page.evaluate("document.querySelector('input[type=\"submit\"]').click()")

    # If we're not auth'd, this will say "Log in | ...":
    assert page.title() == "Site administration | Django site admin"
