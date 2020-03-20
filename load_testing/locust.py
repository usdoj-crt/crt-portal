import os
import random

from locust import HttpLocust, TaskSet, between
from faker import Faker
fake = Faker()

load_tester = os.environ.get('LOAD_TESTER')
load_password = os.environ.get('LOAD_TEST_PASSWORD')

# can't use lazy translated strings outside of django
sections = ['ADM', 'APP', 'CRM', 'DRS', 'ELS', 'EOS', 'FCS', 'HCE', 'IER', 'SPL', 'VOT']
statuses = ['new', 'open', 'closed']
states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]
test_names = ['Liam', 'Charlotte', 'Oliver', 'Amelia', 'Emilia', 'Theodore', 'Violet', 'Declan', 'Aria']


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
    response = l.client.get('/accounts/logout/')


def index(l):
    l.client.get("/form/view")


def random_searches(l):
    # lists the search term and the possible choices
    search_terms = [
        ['assigned_section', sections],
        ['status', statuses],
        ['location_state', states],
        ['contact_first_name', test_names],
        ['contact_last_name', test_names],
        ['location_city_town', test_names],
        ['page', range(1, 10)],
    ]
    last_search_index = len(search_terms) - 1

    url = "/form/view?"
    # picks a random number of arguments to add

    rand = random.randint(1, last_search_index)

    # picks a random number of loops
    for loop in range(0, rand):
        # picks a search at random
        random_choice = random.randint(1, last_search_index)
        search_for = search_terms[random_choice]
        term = search_for[0]
        choices = search_for[1]
        # adds a random value for each argument
        last_choice_index = len(choices) - 1
        value = choices[random.randint(0, last_choice_index)]
        url = f'{url}{term}={value}&'

    l.client.get(url)


def view_details(l):
    response = l.client.get('/form/view/1/')


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


def report(l):
    l.client.get("/report")


class UserBehavior(TaskSet):
    # want to start with low increments so we know the report exists
    report_number = 0
    tasks = {
        index: 2,
        random_searches: 2,
        comment: 1,
        report: 1,
        view_details: 1,
    }

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)