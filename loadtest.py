"""

 $ locust -f loadtest.py --host=https://rfr.herokuapp.com

 $ locust -f loadtest.py --host=http://127.0.0.1:5000

"""
from locust import HttpLocust, TaskSet, task

host_1 = 'https://rfr.herokuapp.com'
host_2 = 'http://127.0.0.1'


class WebsiteTasks(TaskSet):
    def on_start(self):
        self.client.post("/login", {
            "username": "test_user",
            "password": ""
        })

    @task
    def index(self):
        self.client.get("/")

    @task
    def about(self):
        self.client.get("/api/v1/euro/curve/latest/")

    @task
    def about(self):
        self.client.get("/api/v1/euro/curve/single/latest?strip=py_3m")


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000
