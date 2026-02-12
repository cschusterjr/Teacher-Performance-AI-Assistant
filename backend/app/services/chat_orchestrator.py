"""
Chat orchestrator: routes teacher questions to the right analytical function.

This is the "brain" that makes your chatbot feel intelligent even without an LLM.

Later upgrades:
- Replace the router with an LLM function-calling agent.
- Keep the same tools/services so your architecture scales.
"""

from __future__ import annotations
import re
import pandas as pd
from typing import Dict, Tuple

from .analytics import student_snapshot, grade_drivers, struggling_students
from .prescriptive import recommendations
from .predictive import GradePredictor
from .rag import MiniRetriever


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def route_intent(message: str) -> str:
    m = normalize(message)
    if "how is" in m and "doing" in m:
        return "student_status"
    if "pulling" in m and "grade" in m:
        return "grade_drivers"
    if "which students" in m and ("struggling" in m or "failing" in m):
        return "struggling_students"
    if "key assignments" in m and ("struggled" in m or "hard" in m):
        return "hard_assignments"
    if "by the end" in m or "will" in m and ("pass" in m or "fail" in m or "final" in m):
        return "predict_outcome"
    if "recommendation" in m or ("given" in m and "failing" in m):
        return "prescribe"
    return "fallback"


def extract_student_id(message: str) -> str | None:
    # Accept formats like S100123 or "student S100123"
    m = re.search(r"(S\d{6,})", message)
    return m.group(1) if m else None


def answer(
    df_students: pd.DataFrame,
    df_assignments: pd.DataFrame,
    course_id: str,
    message: str,
    predictor: GradePredictor,
    retriever: MiniRetriever,
) -> Tuple[str, Dict[str, str], list[str]]:
    intent = route_intent(message)
    cited: Dict[str, str] = {}
    followups: list[str] = []

    sid = extract_student_id(message)

    if intent in ("student_status", "grade_drivers", "predict_outcome", "prescribe") and not sid:
        return (
            "I can help—what is the student_id? (Example: S100123)",
            {},
            ["How is student S100123 doing?", "What is pulling student S100123's grade down?"]
        )

    if intent == "student_status":
        snap = student_snapshot(df_students, course_id, sid)
        cited["student_snapshot"] = str(snap)
        followups = [
            f"What is pulling {sid}'s grade down?",
            f"How will {sid} do by the end of the course?",
        ]
        return (
            f"Student {sid} currently has a {snap['current_grade']:.1f}% with "
            f"{snap['attendance_rate']:.0%} attendance and {snap['missing_assignments']} missing assignments. "
            f"Recent activity: {snap['recent_activity']} logins in the last 7 days.",
            cited,
            followups,
        )

    if intent == "grade_drivers":
        drivers = grade_drivers(df_students, course_id, sid)
        cited["grade_drivers"] = str(drivers)
        bullets = "\n".join([f"- **{d['factor']}** ({d['severity']}): {d['detail']}" for d in drivers["drivers"]]) or "- No major drivers detected."
        followups = [
            f"Give recommendations to help {sid} pass.",
            "Which students are struggling in this course?",
        ]
        return (
            f"Here are the main factors pulling {sid}'s grade down:\n{bullets}",
            cited,
            followups,
        )

    if intent == "struggling_students":
        struggling = struggling_students(df_students, course_id, threshold=70.0).head(10)
        cited["struggling_students_top10"] = struggling[["student_id", "current_grade"]].to_csv(index=False)
        followups = ["What are key assignments students struggled with?", "Pick a student_id and ask why they're struggling."]
        if struggling.empty:
            return ("No students are currently below 70% in this course.", cited, followups)
        ids = ", ".join(struggling["student_id"].tolist())
        return (f"Students currently struggling (below 70%): {ids}", cited, followups)

    if intent == "hard_assignments":
        # Use assignment table directly for now
        sub = df_assignments[df_assignments["course_id"] == course_id].copy()
        hard = sub.sort_values("avg_score").head(5)
        cited["hardest_assignments"] = hard.to_csv(index=False)
        followups = ["Which students struggled the most on assignment A3?", "What skills are required for the hardest assignments?"]
        names = "\n".join([f"- {r.assignment_name} (avg {r.avg_score:.1f}, submit {r.submission_rate:.0%})" for r in hard.itertuples()])
        return (f"Hardest assignments in the course:\n{names}", cited, followups)

    if intent == "predict_outcome":
        row = df_students[(df_students["course_id"] == course_id) & (df_students["student_id"] == sid)]
        if row.empty:
            return (f"I can't find {sid} in course {course_id}.", {}, [])
        r = row.iloc[0]
        pred = predictor.predict_final_grade(r)
        p_fail = predictor.prob_fail(pred, pass_cutoff=60.0)
        cited["prediction_inputs"] = r.to_dict().__repr__()
        followups = [f"What can we do to help {sid} improve?", f"What is pulling {sid}'s grade down?"]
        status = "pass" if pred >= 60 else "fail"
        return (
            f"Projected final grade for {sid} is **{pred:.1f}%** (likely to **{status}**). "
            f"Estimated probability of failing: **{p_fail:.0%}**.",
            cited,
            followups,
        )

    if intent == "prescribe":
        row = df_students[(df_students["course_id"] == course_id) & (df_students["student_id"] == sid)]
        if row.empty:
            return (f"I can't find {sid} in course {course_id}.", {}, [])
        recs = recommendations(row.iloc[0])
        cited["recommendations"] = str(recs)
        bullets = "\n".join([f"- **{r['priority'].upper()}**: {r['action']} — {r['details']}" for r in recs])
        followups = [f"Which assignment patterns explain {sid}'s struggles?", "Which students are struggling overall?"]
        return (f"Recommendations to help {sid} move to passing:\n{bullets}", cited, followups)

    # Fallback: provide retrieved “course notes”
    hits = retriever.retrieve(message, k=3)
    if hits:
        cited["retrieved_notes"] = "\n\n".join([f"[{doc_id}] {doc}" for doc_id, doc in hits])
        return (
            "I can answer student and course performance questions. Based on your question, here are relevant course notes:\n\n"
            + "\n\n".join([f"- {doc}" for _, doc in hits])
            + "\n\nTry asking: “How is student S100123 doing?” or “Which students are struggling?”",
            cited,
            ["How is student S100123 doing?", "Which students are struggling?", "What is pulling student S100123's grade down?"],
        )

    return (
        "I can help with questions like:\n"
        "- How is student S100123 doing?\n"
        "- What is pulling student S100123's grade down?\n"
        "- Which students are struggling?\n"
        "- What assignments are hardest?\n"
        "- How will student S100123 do by end of course?\n"
        "- What recommendations help student S100123 pass?",
        {},
        ["How is student S100123 doing?", "Which students are struggling?"],
    )
