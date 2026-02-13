# 🧑‍🏫 Teacher Performance AI Assistant

An AI-powered teacher assistant that answers key questions about student performance using descriptive analytics, predictive modeling, and prescriptive recommendations — delivered through a chat-based interface and interactive UI.

This project demonstrates applied machine learning, AI system design, analytics engineering, and scalable backend development in an education-focused use case.

---

## 🎯 Problem

Teachers frequently need fast, reliable answers to performance questions such as:

1. How is student X doing in my course?
2. What is pulling student Y’s grade down?
3. Which students are struggling?
4. What assignments are students struggling with most?
5. How will student Z perform by the end of the course?
6. If student A is failing, what specific actions can help them reach passing?

This assistant transforms raw student signals into actionable insight.

> ⚠️ All data in this repository is synthetic and generated programmatically.

---

## 🧠 What This Project Demonstrates

- Requirement-driven AI development
- Tool-based AI chat orchestration
- Predictive analytics (final grade forecasting)
- Prescriptive analytics (targeted intervention recommendations)
- Descriptive analytics (course and student insights)
- Modular backend architecture (FastAPI)
- Teacher-facing UI (Streamlit)
- API load testing (Locust)
- CI integration (GitHub Actions)

---

## 🏗 Architecture Overview

```
Teacher-Performance-AI-Assistant/
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── main.py         # API entrypoint
│   │   ├── settings.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── analytics.py
│   │       ├── predictive.py
│   │       ├── prescriptive.py
│   │       ├── rag.py
│   │       └── chat_orchestrator.py
│   └── requirements.txt
│
├── ui/                     # Streamlit teacher UI
│   ├── streamlit_app.py
│   └── requirements.txt
│
├── scripts/
│   └── generate_synthetic_data.py
│
├── loadtest/
│   └── locustfile.py
│
└── data/
    └── synthetic_course_data.csv
```

### System Flow

1. Teacher submits question in chat UI
2. Backend detects intent
3. Request is routed to analytics/predictive/prescriptive service
4. Model or rules generate response
5. Structured answer returned with suggested follow-ups

This mirrors real AI agent architecture with tool routing.

---

## 📊 Analytics Capabilities

### 1️⃣ Descriptive Analytics
- Student performance snapshot
- Grade component breakdown
- Identification of struggling students
- Identification of hardest assignments

### 2️⃣ Predictive Analytics
- RandomForest regression model predicts final grade
- Probability of failing derived from predicted grade
- Portfolio-friendly approach that balances interpretability and performance

### 3️⃣ Prescriptive Analytics
- Structured intervention recommendations
- Prioritized by impact (attendance, missing work, exam weakness, etc.)
- Designed for explainability and actionability

---

## 🧪 Synthetic Dataset

The dataset simulates:
- Attendance patterns
- Missing assignments
- Late submissions
- Quiz/homework/exam averages
- Platform engagement
- Assignment difficulty and submission rates

Generated using:

```bash
python scripts/generate_synthetic_data.py
```

No real student data is used.

---

## 🚀 How to Run (On Your Personal Machine)

### Step 1 — Generate Data

```bash
python scripts/generate_synthetic_data.py
```

Creates:

```
data/synthetic_course_data.csv
```

---

### Step 2 — Start Backend API

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

Run API:

```bash
uvicorn backend.app.main:app --reload
```

Health check:

```
http://localhost:8000/health
```

---

### Step 3 — Start Teacher UI

Open a new terminal:

```bash
pip install -r ui/requirements.txt
streamlit run ui/streamlit_app.py
```

---

## 💬 Example Prompts

Use course IDs like `C1` and student IDs like `S100100`.

- How is student S100100 doing in my course?
- What is pulling student S100120's grade down?
- Which students are struggling?
- What are the hardest assignments in this course?
- How will student S100100 do by the end of the course?
- Given student S100120 is failing, what recommendations can help?

---

## 📈 Load Testing

This project includes a Locust load test for scalability simulation.

Install Locust:

```bash
pip install locust
```

Run load test:

```bash
locust -f loadtest/locustfile.py --host http://localhost:8000
```

This simulates multiple teachers interacting with the assistant.

---

## 🔬 Model Strategy

- Model Type: RandomForestRegressor
- Features:
  - Current grade
  - Attendance rate
  - Missing assignments
  - Late submissions
  - Quiz/HW/Exam averages
  - Engagement signals
- Target:
  - Final course grade

Failure probability is derived using a smooth logistic-style mapping around the pass threshold.

This approach is intentionally interpretable and extensible.

---

## 🛠 Tech Stack

- Python 3.10+
- FastAPI
- Streamlit
- scikit-learn
- pandas / numpy
- Uvicorn
- Locust (load testing)
- GitHub Actions (CI)

---

## 📌 Why This Project Is Portfolio-Ready

This repository demonstrates:

- End-to-end AI system design
- Clean modular architecture
- Predictive + prescriptive reasoning
- Chat-based AI orchestration
- Backend + UI integration
- Testing and CI
- Scalability awareness

It reflects how AI systems are built in production environments, not just notebooks.

---

## 🔮 Future Enhancements

- Replace heuristic routing with LLM function-calling agent
- Add real RAG with embeddings and vector store
- Improve model calibration
- Add user authentication
- Containerize with Docker
- Deploy to cloud infrastructure

---

## 📄 Disclaimer

All data in this project is synthetic and generated for demonstration purposes only.
