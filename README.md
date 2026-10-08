# ✈️ DeadlinePilot AI

**Autonomous Academic Assistant & Workload Scheduler**  
*Built for the Hackathon Challenge: **AI Personal Assistant & Autonomous Agents***

---

## 🎯 Overview

**DeadlinePilot AI** is an autonomous productivity agent designed to help students conquer academic overwhelm, overlapping deadlines, and executive dysfunction. 

When facing multiple exams, lab assignments, group projects, and problem sets, students often suffer from decision paralysis and struggle to estimate workload effort or plan around hard deadlines. **DeadlinePilot AI** takes an unstructured description of student commitments, extracts tasks and dates, breaks down complex projects into subtasks, detects scheduling bottlenecks, and synthesizes an achievable daily study plan—complete with a mandatory **Human-in-the-Loop Approval Step**.

---

## 🚀 Key Features & Capabilities

- **Autonomous 7-Step Agent Pipeline**: Executes a multi-stage reasoning and validation pipeline with real-time status visibility.
- **Powered by Official Google Gemini SDK**: Uses `google-genai` with structured JSON output configurations.
- **Priority Matrix Classifier**: Automatically computes task priority levels (**CRITICAL**, **HIGH**, **MEDIUM**, **LOW**) based on deadline proximity, task type (exam vs reading), and estimated effort.
- **Subtask Decomposition**: Automatically decomposes complex tasks (>1.5 hours) into manageable subtask chunks (30 minutes to 2 hours).
- **Conflict & Bottleneck Detection Engine**: Detects overloaded days, tight deadline clusters, and missed/overdue commitments.
- **Schedule Audit & Validation**: Verifies that generated daily schedules respect daily study capacity limits and do not schedule tasks past their deadlines.
- **Human-in-the-Loop Approval Gating**: Requires explicit user approval (**APPROVE PLAN** button) before releasing the final interactive execution checklist.
- **Resilient API Error Handling**: Gracefully handles Gemini API rate limits, 503 service overloads, and missing keys without crashing.

---

## 🔄 Autonomous Agent Workflow Pipeline

The application features a clear 7-step autonomous agent workflow displayed directly in the Streamlit UI:

```
[1. Understanding request] 
       ↓
[2. Extracting tasks] 
       ↓
[3. Detecting deadlines] 
       ↓
[4. Calculating priorities] 
       ↓
[5. Breaking down tasks] 
       ↓
[6. Checking conflicts] 
       ↓
[7. Generating schedule]
       ↓
[Human Approval Gating: APPROVE PLAN]
       ↓
[Locked Interactive Execution Checklist]
```

1. **Understanding Request**: Parses unstructured input text.
2. **Extracting Tasks**: Extracts task titles, types, descriptions, raw deadlines, effort estimates, and dependencies using Gemini API.
3. **Detecting Deadlines**: Converts relative dates (e.g., "in 2 days", "next Friday") into concrete ISO date strings (`YYYY-MM-DD`).
4. **Calculating Priorities**: Evaluates deadline urgency and assigns **CRITICAL**, **HIGH**, **MEDIUM**, or **LOW** priority badges.
5. **Breaking Down Tasks**: Splits large projects into bite-sized actionable subtasks (<2 hours each).
6. **Checking Conflicts**: Identifies daily hour overloads (> daily max capacity) and deadline stacking.
7. **Generating Schedule**: Allocates subtasks into daily time blocks.

---

## 📁 Repository Structure

```text
DeadlinePilot-AI/
├── app.py           # Streamlit Web Application & UI Dashboard
├── agent.py         # DeadlinePilotAgent core class (google-genai workflow)
├── prompts.py       # Gemini API prompts and JSON schema templates
├── tools.py         # Priority calculation, conflict detector, schedule validator
├── requirements.txt # Python package dependencies
├── .env             # Environment variables configuration (GEMINI_API_KEY, GEMINI_MODEL)
├── .gitignore       # Git ignore rules for sensitive files
└── README.md        # Project documentation
```

---

## ⚙️ Installation & Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DeadlinePilot-AI.git
cd DeadlinePilot-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory (do **NOT** commit this file):
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

*Note: If `GEMINI_MODEL` is not set, DeadlinePilot AI defaults to `gemini-3.8-flash`. You can also enter or override your API Key directly in the Streamlit UI sidebar.*

---

## 🏃 Running the Application

Launch the Streamlit web application:
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🎬 Hackathon Demonstration Guide

1. **Load Sample Student Scenario**: Click the **📚 Load Student Demo Scenario** button in the UI. This populates a realistic student workload containing:
   - Data Structures Midterm Exam in 2 days (8 hrs study)
   - OS Lab 3 due in 3 days (6 hrs)
   - Software Engineering Group Project due in 4 days (4 hrs)
   - Linear Algebra Problem Set due tomorrow (3 hrs)
   - Technical Writing Quiz in 5 days (1.5 hrs)
2. **Launch Agent**: Click **🚀 Launch DeadlinePilot Agent**.
3. **Observe Workflow**: Watch the 7-step autonomous agent pipeline execute in real time.
4. **Review Intelligence & Conflicts**: Inspect the extracted task priorities (**CRITICAL** badges), subtask breakdowns, detected workload warnings, and draft daily schedule.
5. **Human-in-the-Loop Approval**: Click **👍 APPROVE PLAN** to lock in the study schedule and view the interactive task execution checklist.

---

## 🛠️ Built With

- **Python 3.10+**
- **Google Gemini API** (`google-genai` SDK)
- **Streamlit** (UI Framework)
- **python-dotenv** (Environment Configuration)
