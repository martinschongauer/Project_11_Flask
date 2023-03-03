from locust import HttpUser, task


class ProjectPerfTest(HttpUser):
    @task
    def index(self):
        response = self.client.get("/")

    @task
    def board(self):
        response = self.client.get("/printClubs")

    @task
    def logout(self):
        response = self.client.get("/logout")

    @task
    def book(self):
        response = self.client.get("/book/Spring%20Festival/Simply%20Lift")

    @task
    def purchase(self):
        response = self.client.post("/purchasePlaces", data=
                                    {
                                        "competition": "Spring Festival",
                                        "club": "Simply Lift",
                                        "places": "0"
                                    }
                                    )

    @task
    def summary(self):
        response = self.client.post("/showSummary", data=
                                    {
                                        "email": "john@simplylift.co"
                                    }
                                    )
