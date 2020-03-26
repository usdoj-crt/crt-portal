import os
import random

from locust import HttpLocust, TaskSet, between
from faker import Faker

from load_test_data import SECTIONS, STATUSES, STATES, TEST_NAMES, random_form

fake = Faker()

load_tester = os.environ.get('LOAD_TESTER')
load_password = os.environ.get('LOAD_TEST_PASSWORD')


def login(l):
    # login to the application
    response = l.client.get('/accounts/login/')
    csrftoken = response.cookies['csrftoken']
    l.client.post(
        '/accounts/login/',
        {'username': load_tester, 'password': load_password},
        headers={
            'X-CSRFToken': csrftoken,
            'Referer': l.client.base_url,
        },
    )


def logout(l):
    l.client.get('/accounts/logout/')


def index(l):
    l.client.get("/form/view")


def random_searches(l):
    url = "/form/view?"
    # lists the search term and the possible choices
    search_terms = [
        ['assigned_section', SECTIONS],
        ['status', STATUSES],
        ['location_state', STATES],
        ['contact_first_name', TEST_NAMES],
        ['contact_last_name', TEST_NAMES],
        ['location_city_town', TEST_NAMES],
        ['page', range(1, 10)],
    ]
    last_search_index = len(search_terms) - 1
    # picks a random number of arguments to add
    rand = random.randint(1, last_search_index)
    # picks a random number of loops
    for loop in range(0, rand):
        # picks a search at random
        search_for = random.choice(search_terms)
        term = search_for[0]
        # adds a random value for each argument
        value = random.choice(search_for[1])
        url = f'{url}{term}={value}&'

    l.client.get(url)


def view_details(l):
    l.client.get('/form/view/1/')


def comment(l):
    response = l.client.get('/form/view/1/')
    csrftoken = response.cookies['csrftoken']
    l.client.post(
        f'/form/comment/report/1/',
        {'is_summary': False, 'note': fake.text()},
        headers={
            'X-CSRFToken': csrftoken,
            'Referer': l.client.base_url,
        },
    )


def pro_form(l):
    response = l.client.get('/form/new/')
    csrftoken = response.cookies['csrftoken']
    data = random_form(0, 0, csrftoken, 'pro')
    l.client.post(
        f'/form/new/',
        data,
        headers={
            'X-CSRFToken': csrftoken,
            'Referer': l.client.base_url,
        },
    )


def get_report(l):
    response = l.client.get('/report/')
    csrftoken = response.cookies['csrftoken']
    sessionid = response.cookies['sessionid']
    # page 1 response
    index = 0

    for step in [0, 1, 2, 8, 9, 10, 11, 12]:
        data = random_form(step, index, csrftoken, 'multi-step')
        response = l.client.post(
            f'/report/',
            data,
            headers={
                'X-CSRFToken': csrftoken,
                'Referer': l.client.base_url,
                'sessionid': sessionid,
            },
        )

        # the confirmation page won't have a cookie
        if 'csrftoken' in response.cookies:
            csrftoken = response.cookies['csrftoken']
            sessionid = response.cookies['sessionid']

        index += 1


class UserBehavior(TaskSet):
    tasks = {
        # index: 2,
        # random_searches: 2,
        # comment: 1,
        # view_details: 1,
        # pro_form: 3,
        get_report: 10,

    }

    # def on_start(self):
    #     login(self)

    # def on_stop(self):
    #     logout(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
