"""
Generates a single CSV that includes both:
- student-level course records (record_type=student)
- assignment-level aggregates (record_type=assignment)

This keeps the project lightweight while still enabling:
- student analytics
- assignment analytics
- prediction of final grade
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def generate(n_students=800, n_courses=3, n_assignments=10, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []

    course_ids = [f"C{i+1}" for i in range(n_courses)]

    # Assignment “difficulty” per course
    for course_id in course_ids:
        for a in range(n_assignments):
            assignment_id = f"A{a+1}"
            difficulty = rng.uniform(0.8, 1.2)  # >1 is harder
            avg_score = np.clip(rng.normal(78 / difficulty, 8), 40, 98)
            submission_rate = np.clip(rng.normal(0.92 - (difficulty - 1) * 0.15, 0.05), 0.5, 1.0)

            rows.append({
                "record_type": "assignment",
                "course_id": course_id,
                "assignment_id": assignment_id,
                "assignment_name": f"Assignment {a+1}",
                "avg_score": float(avg_score),
                "submission_rate": float(submission_rate),
            })

    # Student records
    for course_id in course_ids:
        for i in range(n_students):
            student_id = f"S{100000+i}"
            attendance = np.clip(rng.normal(0.92, 0.06), 0.5, 1.0)
            missing = int(np.clip(rng.poisson(1.8), 0, 12))
            late = int(np.clip(rng.poisson(1.2), 0, 12))
            logins = int(np.clip(rng.poisson(4.5), 0, 30))

            quiz = float(np.clip(rng.normal(78, 10), 20, 100))
            hw = float(np.clip(rng.normal(80, 10), 20, 100))
            exam = float(np.clip(rng.normal(76, 12), 10, 100))

            # Current grade (imperfect, partly based on components + penalties)
            current_grade = (
                0.3 * hw + 0.2 * quiz + 0.4 * exam + 0.1 * (attendance * 100)
                - 1.5 * missing - 0.7 * late
            )
            current_grade = float(np.clip(current_grade, 0, 100))

            # Final grade (some drift)
            drift = rng.normal(0, 6)
            final_grade = float(np.clip(current_grade + drift - 0.8 * missing, 0, 100))

            # Label: at-risk (fail) probability
            lin = (
                2.5 * (0.9 - attendance) +
                0.08 * missing +
                0.04 * late -
                0.02 * logins +
                0.02 * (70 - current_grade) +
                rng.normal(0, 0.3)
            )
            p_fail = sigmoid(lin)
            label = int(rng.binomial(1, p_fail))

            rows.append({
                "record_type": "student",
                "course_id": course_id,
                "student_id": student_id,
                "attendance_rate": attendance,
                "missing_assignments": missing,
                "late_submissions": late,
                "avg_quiz_score": quiz,
                "avg_hw_score": hw,
                "avg_exam_score": exam,
                "logins_last_7d": logins,
                "current_grade": current_grade,
                "final_grade": final_grade,
                "label": label,
            })

    return pd.DataFrame(rows)


def main():
    out = Path("data")
    out.mkdir(parents=True, exist_ok=True)
    df = generate()
    path = out / "synthetic_course_data.csv"
    df.to_csv(path, index=False)
    print(f"Wrote: {path} rows={len(df)}")
    print(df["record_type"].value_counts())


if __name__ == "__main__":
    main()
