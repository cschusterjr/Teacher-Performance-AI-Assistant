from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
from pathlib import Path

from .settings import settings
from .schemas import ChatRequest, ChatResponse, CourseInsightsResponse
from .services.data_repo import CourseDataRepo
from .services.analytics import struggling_students, hardest_assignments
from .services.predictive import GradePredictor, load_predictor, save_predictor
from .services.rag import MiniRetriever
from .services.chat_orchestrator import answer


app = FastAPI(title="Teacher Performance AI Assistant", version="0.1.0")

# Allow local dev UI (Streamlit) to call the API easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup (simple baseline)
repo = CourseDataRepo(data_path=Path(settings.data_path))
df_students: pd.DataFrame | None = None
df_assignments: pd.DataFrame | None = None

predictor: GradePredictor | None = None
retriever: MiniRetriever | None = None


@app.on_event("startup")
def startup():
    global df_students, df_assignments, predictor, retriever

    df = repo.load()

    # students table (one row per student per course)
    df_students = df[df["record_type"] == "student"].copy()

    # assignments aggregated table (one row per assignment per course)
    df_assignments = df[df["record_type"] == "assignment"].copy()

    # Train/load predictor
    artifacts = Path(settings.artifacts_dir)
    model_path = artifacts / "grade_predictor.pkl"
    if model_path.exists():
        predictor = load_predictor(artifacts)
    else:
        predictor = GradePredictor.train(df_students)
        save_predictor(predictor, artifacts)

    # Simple “course notes” corpus for retrieval
    docs = [
        ("course_policy", "Late work is accepted up to 3 days with a 10% penalty per day."),
        ("grading_weights", "Grades are computed from: Homework 30%, Quizzes 20%, Exams 40%, Participation 10%."),
        ("interventions", "High-impact interventions: missing work recovery plan, attendance plan, reteach weak standards."),
    ]
    retriever = MiniRetriever(docs=docs)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    assert df_students is not None and df_assignments is not None
    assert predictor is not None and retriever is not None

    answer_text, cited, followups = answer(
        df_students=df_students,
        df_assignments=df_assignments,
        course_id=req.course_id,
        message=req.message,
        predictor=predictor,
        retriever=retriever,
    )
    return ChatResponse(answer=answer_text, cited_data=cited, suggested_followups=followups)


@app.get("/courses/{course_id}/insights", response_model=CourseInsightsResponse)
def course_insights(course_id: str):
    assert df_students is not None and df_assignments is not None

    struggling = struggling_students(df_students, course_id, threshold=70.0).head(10)
    hard = hardest_assignments(df_assignments, course_id, top_n=5)

    struggling_list = []
    for r in struggling.itertuples():
        struggling_list.append(
            {
                "student_id": r.student_id,
                "current_grade": float(r.current_grade),
                "attendance_rate": float(r.attendance_rate),
                "missing_assignments": int(r.missing_assignments),
                "risk_of_failing": float(max(0.0, min(1.0, (70 - r.current_grade) / 20))),
            }
        )

    return {
        "course_id": course_id,
        "struggling_students": struggling_list,
        "hardest_assignments": hard,
    }
