import pandas as pd
from backend.app.services.analytics import student_snapshot, grade_drivers


def test_student_snapshot():
    df = pd.DataFrame([
        {
            "course_id": "C1",
            "student_id": "S100001",
            "current_grade": 65,
            "attendance_rate": 0.85,
            "missing_assignments": 4,
            "late_submissions": 2,
            "avg_quiz_score": 70,
            "avg_hw_score": 72,
            "avg_exam_score": 60,
            "logins_last_7d": 1,
        }
    ])
    s = student_snapshot(df, "C1", "S100001")
    assert s["student_id"] == "S100001"
    assert s["current_grade"] == 65.0


def test_grade_drivers_has_drivers():
    df = pd.DataFrame([
        {
            "course_id": "C1",
            "student_id": "S100001",
            "current_grade": 65,
            "attendance_rate": 0.85,
            "missing_assignments": 4,
            "late_submissions": 2,
            "avg_quiz_score": 70,
            "avg_hw_score": 72,
            "avg_exam_score": 60,
            "logins_last_7d": 1,
        }
    ])
    d = grade_drivers(df, "C1", "S100001")
    assert len(d["drivers"]) > 0
