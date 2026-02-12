"""
Predictive analytics:
- predict end-of-course grade
- estimate probability of failing

Model strategy (portfolio-friendly):
- train a simple regression model for final_grade
- convert to pass/fail probability using a calibrated rule
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


FEATURES = [
    "current_grade",
    "attendance_rate",
    "missing_assignments",
    "late_submissions",
    "avg_quiz_score",
    "avg_hw_score",
    "avg_exam_score",
    "logins_last_7d",
]


@dataclass
class GradePredictor:
    model: RandomForestRegressor

    @staticmethod
    def train(df: pd.DataFrame) -> "GradePredictor":
        X = df[FEATURES].copy()
        y = df["final_grade"].astype(float)

        # Coerce numerics + simple imputation
        for c in FEATURES:
            X[c] = pd.to_numeric(X[c], errors="coerce")
        X = X.fillna(X.median(numeric_only=True))

        model = RandomForestRegressor(
            n_estimators=400,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X, y)
        return GradePredictor(model=model)

    def predict_final_grade(self, row: pd.Series) -> float:
        X = row[FEATURES].to_frame().T.copy()
        for c in FEATURES:
            X[c] = pd.to_numeric(X[c], errors="coerce")
        X = X.fillna(X.median(numeric_only=True))
        pred = float(self.model.predict(X)[0])
        return float(np.clip(pred, 0, 100))

    def prob_fail(self, predicted_final: float, pass_cutoff: float = 60.0) -> float:
        """
        Simple probability curve around the cutoff.
        Replace later with a classifier + calibration if you want.
        """
        # Logistic-ish mapping: 60 => ~0.5 probability failing
        x = (pass_cutoff - predicted_final) / 6.0
        p = 1 / (1 + np.exp(-x))
        return float(np.clip(p, 0, 1))


def save_predictor(p: GradePredictor, artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(p, artifact_dir / "grade_predictor.pkl")


def load_predictor(artifact_dir: Path) -> GradePredictor:
    return joblib.load(artifact_dir / "grade_predictor.pkl")
