# Teacher Performance AI Assistant (Portfolio Project)

An AI-powered teacher assistant that answers key questions about student performance:

1. How is student X doing in my course?
2. What is pulling student Y's grade down?
3. Which students are struggling?
4. What are key assignments students have struggled with?
5. How will student Z do by end of course (pass/fail/final grade)?
6. Given student A is failing, what recommendations help them reach passing?

## Architecture
- **FastAPI backend**: chat orchestration + analytics + prediction + recommendations
- **Streamlit UI**: teacher-facing chat + course insights
- **Synthetic dataset generator**: realistic course/student signals
- **Predictive analytics**: final grade prediction (regression) + fail risk
- **Prescriptive analytics**: structured recommendations
- **Load testing**: Locust script included

## Setup (later, on your personal machine)
1) Generate synthetic data:
```bash
python scripts/generate_synthetic_data.py
