"""
Descriptive analytics:
- student status
- what is pulling grade down
- who is struggling
- hardest assignments
"""

from __future__ import annotations
import pandas as pd


FEATURE_COLS = [
    "attendance_rate",
    "missing_assignments",
    "late_submissions",
    "avg_quiz_score",
    "avg_hw_score",
    "avg_exam_score",
    "logins_last_7d",
]


def student_snapshot(df: pd.DataFrame, course_id: str, student_id: str) -> dict:
    row = df[(df["course_id"] == course_id) & (df["student_id"] == student_id)]
    if row.empty:
        raise ValueError(f"Student {student_id} not found in course {course_id}.")
    r = row.iloc[0].to_dict()

    return {
        "student_id": student_id,
        "course_id": course_id,
        "current_grade": float(r["current_grade"]),
        "attendance_rate": float(r["attendance_rate"]),
        "missing_assignments": int(r["missing_assignments"]),
        "late_submissions": int(r["late_submissions"]),
        "avg_quiz_score": float(r["avg_quiz_score"]),
        "avg_hw_score": float(r["avg_hw_score"]),
        "avg_exam_score": float(r["avg_exam_score"]),
        "recent_activity": int(r["logins_last_7d"]),
    }


def grade_drivers(df: pd.DataFrame, course_id: str, student_id: str) -> dict:
    """
    Provide a simple, interpretable breakdown for what's likely pulling a grade down.
    This is rule-based on purpose: easy to explain and portfolio-friendly.
    """
    s = student_snapshot(df, course_id, student_id)

    issues = []
    if s["attendance_rate"] < 0.9:
        issues.append({"factor": "attendance", "severity": "high", "detail": f"Attendance is {s['attendance_rate']:.0%}."})
    if s["missing_assignments"] >= 3:
        issues.append({"factor": "missing_assignments", "severity": "high", "detail": f"Missing {s['missing_assignments']} assignments."})
    if s["late_submissions"] >= 3:
        issues.append({"factor": "late_work", "severity": "medium", "detail": f"{s['late_submissions']} late submissions."})
    if s["avg_exam_score"] < 70:
        issues.append({"factor": "exam_performance", "severity": "high", "detail": f"Average exam score {s['avg_exam_score']:.1f}."})
    if s["avg_hw_score"] < 75:
        issues.append({"factor": "homework_performance", "severity": "medium", "detail": f"Average HW score {s['avg_hw_score']:.1f}."})
    if s["avg_quiz_score"] < 75:
        issues.append({"factor": "quiz_performance", "severity": "medium", "detail": f"Average quiz score {s['avg_quiz_score']:.1f}."})
    if s["recent_activity"] < 2:
        issues.append({"factor": "low_platform_engagement", "severity": "medium", "detail": f"Only {s['recent_activity']} logins in last 7 days."})

    issues = sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])
    return {"student_id": student_id, "course_id": course_id, "drivers": issues}


def struggling_students(df: pd.DataFrame, course_id: str, threshold: float = 70.0) -> pd.DataFrame:
    sub = df[df["course_id"] == course_id].copy()
    return sub[sub["current_grade"] < threshold].sort_values("current_grade")


def hardest_assignments(df_assignments: pd.DataFrame, course_id: str, top_n: int = 5) -> list[dict]:
    sub = df_assignments[df_assignments["course_id"] == course_id].copy()
    sub["avg_score"] = sub["avg_score"].astype(float)
    hard = sub.sort_values("avg_score").head(top_n)
    return hard[["assignment_id", "assignment_name", "avg_score", "submission_rate"]].to_dict(orient="records")
