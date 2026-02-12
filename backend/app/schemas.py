from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    teacher_id: str = Field(..., description="Teacher identifier (synthetic in this project).")
    course_id: str = Field(..., description="Course identifier.")
    message: str = Field(..., description="User message to the assistant.")
    history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    cited_data: Dict[str, str] = Field(default_factory=dict)
    suggested_followups: List[str] = Field(default_factory=list)


class StudentSummary(BaseModel):
    student_id: str
    current_grade: float
    attendance_rate: float
    missing_assignments: int
    risk_of_failing: float


class CourseInsightsResponse(BaseModel):
    course_id: str
    struggling_students: List[StudentSummary]
    hardest_assignments: List[dict]
