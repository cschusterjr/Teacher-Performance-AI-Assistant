"""
Prescriptive analytics:
Given student is failing, generate recommended interventions.

This is intentionally:
- explainable
- actionable
- structured
Later: you can augment with an LLM to make the phrasing more natural.
"""

from __future__ import annotations
import pandas as pd


def recommendations(student_row: pd.Series) -> list[dict]:
    recs = []

    attendance = float(student_row["attendance_rate"])
    missing = int(student_row["missing_assignments"])
    late = int(student_row["late_submissions"])
    exam = float(student_row["avg_exam_score"])
    hw = float(student_row["avg_hw_score"])
    quiz = float(student_row["avg_quiz_score"])
    logins = int(student_row["logins_last_7d"])

    # High-impact, common levers first
    if missing >= 3:
        recs.append({
            "priority": "high",
            "action": "Missing work recovery plan",
            "details": "Create a 7-day plan to complete missing assignments. Offer partial credit and office hours."
        })
    if attendance < 0.9:
        recs.append({
            "priority": "high",
            "action": "Attendance intervention",
            "details": "Identify pattern (days/times). Contact guardian/counselor. Set attendance goal + check-ins."
        })
    if exam < 70:
        recs.append({
            "priority": "high",
            "action": "Exam prep + reteach plan",
            "details": "Assign targeted practice on weak standards; retake opportunities; short daily retrieval practice."
        })
    if hw < 75 or quiz < 75:
        recs.append({
            "priority": "medium",
            "action": "Practice scaffolding",
            "details": "Shorten assignments, provide exemplars, and use spaced practice. Add 2 quick formative checks weekly."
        })
    if late >= 3:
        recs.append({
            "priority": "medium",
            "action": "Time management supports",
            "details": "Break tasks into milestones with due dates; allow structured extensions; teach planning routines."
        })
    if logins < 2:
        recs.append({
            "priority": "medium",
            "action": "Engagement nudge",
            "details": "Set a weekly platform routine; send reminders; assign a short mandatory check-in activity."
        })

    if not recs:
        recs.append({
            "priority": "low",
            "action": "General support",
            "details": "Schedule a student conference and set two measurable goals for the next 2 weeks."
        })

    # Sort: high first
    order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: order[r["priority"]])
    return recs
