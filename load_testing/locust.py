import os

from locust import HttpLocust, TaskSet, between

load_tester = os.environ.get('LOAD_TESTER')
load_password = os.environ.get('LOAD_TEST_PASSWORD')


def login(l):
    response = l.client.get('/accounts/login/')
    csrftoken = response.cookies['csrftoken']
    l.client.post("/accounts/login/?next=/form/view/", {"username": load_tester, "password": load_password}, headers={'X-CSRFToken': csrftoken})


def logout(l):
    l.client.post("/accounts/logout/", {"username": load_tester, "password": load_password})


def index(l):
    l.client.get("/form/view")


def report(l):
    l.client.get("/report")


class UserBehavior(TaskSet):
    tasks = {index: 2, report: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)