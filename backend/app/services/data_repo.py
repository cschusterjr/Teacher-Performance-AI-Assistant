"""
Data access layer.

Today: reads a CSV (synthetic dataset).
Tomorrow: swap this to a database without rewriting your analytics code.
"""

from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from pathlib import Path


@dataclass(frozen=True)
class CourseDataRepo:
    data_path: Path

    def load(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Data file not found: {self.data_path}. "
                f"Generate it with scripts/generate_synthetic_data.py"
            )
        df = pd.read_csv(self.data_path)
        return df
