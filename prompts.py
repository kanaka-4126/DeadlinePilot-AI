"""
Prompt templates and definitions for DeadlinePilot AI using Google Gemini API.
"""

SYSTEM_PROMPT = """You are DeadlinePilot AI, an autonomous productivity assistant specialized in academic workload management and executive function support for students.
Your core mission is to analyze unstructured student commitments (assignments, exams, projects, labs, personal duties) and convert them into structured, realistic, prioritized action plans.

Guidelines:
1. Always be objective, practical, and precise with time estimates.
2. Break down complex tasks into subtasks that take between 30 minutes and 2 hours each.
   - For a Data Structures & Algorithms (DSA) Midterm Exam, prep MUST explicitly include: Big-O notation, Trees, Graphs, Dynamic Programming, and a Practice/mock exam.
3. TIME WINDOW & EVENT RESERVATIONS:
   - If an exam is on Friday morning (date D), ALL exam preparation MUST be completed BEFORE Friday morning (on Wednesday and Thursday).
   - Reserve the exam event time itself on Friday morning as UNAVAILABLE for study.
   - Do NOT schedule preparation for an exam after the exam has started.
   - Schedule prerequisite/lab work (e.g. OS Lab) AFTER associated exams (e.g. Friday Afternoon onwards).
   - Lower priority tasks (e.g. Technical Writing) should be deferred until after earlier urgent deadlines.
4. Respect daily capacity limits. If workload exceeds capacity before a deadline, place unassigned sessions into unassigned_tasks and specify which lower-priority tasks should be deferred.
5. Do NOT include any meta-reasoning, chain-of-thought, or internal commentary. Output ONLY clean JSON matching the requested format.
"""

EXTRACTION_PROMPT_TEMPLATE = """Analyze the following student workload text and extract all tasks, deadlines, estimated effort, and dependencies.

Current Reference Date: {current_date}

User Input:
\"\"\"
{user_input}
\"\"\"

Return a JSON object matching this exact schema:
{{
  "summary": "Short 1-2 sentence overview of the student's workload",
  "tasks": [
    {{
      "id": "TASK_1",
      "title": "Clear concise task name",
      "task_type": "exam | assignment | project | lab | reading | personal",
      "description": "Brief summary of what needs to be done",
      "raw_deadline": "Original deadline text from user input",
      "deadline_iso": "YYYY-MM-DD (calculated based on reference date, or null if unknown)",
      "estimated_hours": 3.5,
      "urgency_notes": "Why this task is urgent or important",
      "dependencies": ["ID of prerequisite task if any, e.g. TASK_0"]
    }}
  ]
}}
"""

BREAKDOWN_PROMPT_TEMPLATE = """Given the extracted tasks for a student, break down any complex task (estimated > 1.5 hours) into smaller, actionable subtasks (30m - 2h each).

Special Breakdown Requirements:
- For Data Structures & Algorithms (DSA) Midterm Exam, subtasks MUST include:
  1. Big-O Notation & Complexity Analysis
  2. Trees & Binary Search Trees
  3. Graphs & Traversal Algorithms (BFS/DFS)
  4. Dynamic Programming Concepts
  5. Practice & Mock Midterm Exam

Tasks to analyze:
{tasks_json}

Return a JSON object with this exact schema:
{{
  "task_breakdowns": [
    {{
      "task_id": "TASK_1",
      "subtasks": [
        {{
          "subtask_id": "TASK_1_SUB_1",
          "title": "Subtask title",
          "estimated_hours": 1.0,
          "order": 1
        }}
      ]
    }}
  ]
}}
"""

SCHEDULING_PROMPT_TEMPLATE = """Generate a realistic, day-by-day study schedule for the student based on their tasks, subtasks, priorities, and daily available study capacity.

Current Reference Date: {current_date}
Max Daily Study Capacity: {max_daily_hours} hours per day

STRICT EVENT & TIME-WINDOW RULES:
1. FRIDAY MORNING EXAM RESERVATION:
   - Friday morning is the DSA Midterm Exam event itself. Reserve Friday morning as UNAVAILABLE for study.
   - ALL DSA exam prep (Big-O, Trees, Graphs, Dynamic Programming, Practice Exam) MUST be scheduled on Wednesday and Thursday BEFORE Friday morning.
2. LINEAR ALGEBRA DEADLINE:
   - Linear Algebra Problem Set is due Thursday 11:59 PM. Must be completed on Wednesday/Thursday.
3. OS LAB DEPENDENCY & SEQUENCING:
   - OS Lab work must be scheduled AFTER the DSA exam (Friday afternoon/evening and Saturday) and completed before Saturday midnight.
4. SOFTWARE ENGINEERING DEADLINE:
   - Software Engineering project work must be completed before Sunday 5 PM.
5. TECHNICAL WRITING DEFERRAL:
   - Technical Writing Reading & Quiz can be deferred to Sunday/Monday after earlier urgent deadlines.
6. CAPACITY OVERFLOW & DEFERRALS:
   - If workload cannot fit within {max_daily_hours}h/day before deadlines, place excess sessions in "unassigned_tasks" and explicitly identify which lower-priority tasks should be deferred.

Tasks & Subtasks:
{tasks_with_subtasks_json}

Priorities & Conflicts Identified:
{conflicts_info_json}

Return a JSON object matching this exact schema:
{{
  "schedule_strategy": "Summary of the scheduling strategy employed",
  "daily_schedule": [
    {{
      "date": "YYYY-MM-DD",
      "day_name": "Monday / Tuesday / etc.",
      "total_hours": 4.5,
      "items": [
        {{
          "task_id": "TASK_1",
          "subtask_id": "TASK_1_SUB_1",
          "title": "What to work on",
          "duration_hours": 1.5,
          "time_block": "Morning / Afternoon / Evening",
          "focus_note": "Key goal for this session"
        }}
      ]
    }}
  ],
  "unassigned_tasks": [
    {{
      "task_id": "TASK_ID",
      "title": "Task Title",
      "duration_hours": 2.0,
      "reason": "Explanation of capacity bottleneck before deadline",
      "deferral_recommendation": "Which lower priority work to defer"
    }}
  ]
}}
"""
