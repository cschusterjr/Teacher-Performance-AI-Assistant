from locust import HttpUser, task, between

class TeacherAssistantUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def chat_student_status(self):
        payload = {
            "teacher_id": "T1",
            "course_id": "C1",
            "message": "How is student S100100 doing in my course?",
            "history": []
        }
        self.client.post("/chat", json=payload)

    @task
    def chat_grade_drivers(self):
        payload = {
            "teacher_id": "T1",
            "course_id": "C1",
            "message": "What is pulling student S100120's grade down?",
            "history": []
        }
        self.client.post("/chat", json=payload)

    @task
    def insights(self):
        self.client.get("/courses/C1/insights")
