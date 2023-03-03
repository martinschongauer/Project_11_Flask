from locust import HttpUser, task


class ProjectPerfTest(HttpUser):
    @task
    def index(self):
        response = self.client.get("/printClubs")

    @task(3)
    def board(self):
        response = self.client.get("/printClubs")
