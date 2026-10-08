"""
DeadlinePilot Agent core engine using official google-genai SDK with Local Demo Mode fallback support.
"""

import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.errors import APIError

from prompts import (
    SYSTEM_PROMPT,
    EXTRACTION_PROMPT_TEMPLATE,
    BREAKDOWN_PROMPT_TEMPLATE,
    SCHEDULING_PROMPT_TEMPLATE
)
from tools import (
    calculate_priorities,
    detect_conflicts,
    validate_schedule,
    clean_json_response,
    audit_and_fix_schedule,
    ensure_dsa_subtasks,
    resolve_deadline_date,
    get_local_demo_results
)

# Load environment variables
load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


class DeadlinePilotAgent:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
        self.client = None

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def _call_gemini(self, prompt, system_instruction=None):
        """
        Internal wrapper to execute Gemini model calls using google-genai SDK.
        Handles API errors, 503 service unavailable, rate limits, and missing keys.
        """
        if not self.client:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is missing. Switching to Local Demo Mode.")
            self.client = genai.Client(api_key=self.api_key)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction or SYSTEM_PROMPT,
            temperature=0.2,
            response_mime_type="application/json"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except APIError as e:
            if e.code == 429 or "quota" in str(e).lower() or "429" in str(e):
                raise RuntimeError("Gemini API quota exceeded (429). Switching to Local Demo Mode.") from e
            elif e.code == 503 or "503" in str(e):
                raise RuntimeError("Gemini Service is temporarily unavailable (503). Switching to Local Demo Mode.") from e
            elif e.code == 400 or "API_KEY" in str(e):
                raise RuntimeError("Invalid or missing Gemini API Key. Switching to Local Demo Mode.") from e
            else:
                raise RuntimeError(f"Gemini API Error [{e.code}]: {e.message}") from e
        except Exception as e:
            raise RuntimeError(f"Communication error with Gemini API: {str(e)}") from e

    def run_workflow_stream(self, user_input, current_date=None, max_daily_hours=6.0, force_demo=False):
        """
        Executes the 7-step autonomous agent workflow.
        Supports seamless fallback to Local Demo Mode if force_demo=True or Gemini API hits rate/quota limits.
        """
        if not current_date:
            current_date = datetime.now().strftime("%Y-%m-%d")

        # Step 1: Understanding request
        yield {
            "step": 1,
            "name": "Understanding request",
            "status": "in_progress",
            "detail": "Analyzing unstructured student workload input..."
        }

        if not user_input or len(user_input.strip()) < 10:
            yield {
                "step": 1,
                "name": "Understanding request",
                "status": "error",
                "detail": "Input text is too short. Please provide details on your tasks, deadlines, and exams."
            }
            return

        yield {
            "step": 1,
            "name": "Understanding request",
            "status": "completed",
            "detail": f"Parsed input request ({len(user_input)} characters)."
        }

        # If user explicitly requested Local Demo Mode or API Key is missing, run Local Demo Mode directly
        if force_demo or not self.api_key:
            demo_results = get_local_demo_results(current_date, max_daily_hours)

            # Step 2: Extracting tasks (Local Demo)
            yield {
                "step": 2,
                "name": "Extracting tasks",
                "status": "completed",
                "detail": f"[Demo Mode] Extracted {len(demo_results['tasks'])} commitments from student scenario."
            }

            # Step 3: Detecting deadlines (Local Demo)
            yield {
                "step": 3,
                "name": "Detecting deadlines",
                "status": "completed",
                "detail": f"[Demo Mode] Resolved hard deadlines relative to reference date {current_date}."
            }

            # Step 4: Calculating priorities (Local Demo)
            yield {
                "step": 4,
                "name": "Calculating priorities",
                "status": "completed",
                "detail": "[Demo Mode] Categorized priorities: DSA Midterm & Lin Alg (CRITICAL), OS Lab & SE Project (HIGH)."
            }

            # Step 5: Breaking down tasks (Local Demo)
            yield {
                "step": 5,
                "name": "Breaking down tasks",
                "status": "completed",
                "detail": "[Demo Mode] Decomposed DSA prep into 5 topic modules (Big-O, Trees, Graphs, DP, Mock Exam)."
            }

            # Step 6: Checking conflicts (Local Demo)
            yield {
                "step": 6,
                "name": "Checking conflicts",
                "status": "completed",
                "detail": "[Demo Mode] Identified workload bottleneck (11.0h required vs 6.0h/day capacity limit)."
            }

            # Step 7: Generating schedule (Local Demo)
            yield {
                "step": 7,
                "name": "Generating schedule",
                "status": "completed",
                "detail": "[Demo Mode] Generated date-aligned schedule with Friday morning exam reservation."
            }

            yield {
                "step": 8,
                "name": "Workflow Complete",
                "status": "finished",
                "detail": "Local Demo Mode workflow completed successfully.",
                "results": demo_results
            }
            return

        # Attempt Gemini-powered workflow execution
        workflow_results = {
            "is_demo_mode": False,
            "summary": "",
            "tasks": [],
            "prioritized_tasks": [],
            "task_breakdowns": {},
            "conflicts": [],
            "schedule": {},
            "validation": {}
        }

        try:
            # Step 2: Extracting tasks
            yield {
                "step": 2,
                "name": "Extracting tasks",
                "status": "in_progress",
                "detail": "Extracting commitments, estimated hours, and raw deadlines..."
            }

            extraction_prompt = EXTRACTION_PROMPT_TEMPLATE.format(
                current_date=current_date,
                user_input=user_input
            )
            raw_ext = self._call_gemini(extraction_prompt)
            extracted_data = clean_json_response(raw_ext)
            
            tasks = extracted_data.get("tasks", [])
            summary = extracted_data.get("summary", "Workload extracted.")
            workflow_results["summary"] = summary
            workflow_results["tasks"] = tasks

            yield {
                "step": 2,
                "name": "Extracting tasks",
                "status": "completed",
                "detail": f"Extracted {len(tasks)} distinct tasks from student description."
            }

            # Step 3: Detecting deadlines
            yield {
                "step": 3,
                "name": "Detecting deadlines",
                "status": "in_progress",
                "detail": "Parsing relative dates into structured ISO deadlines..."
            }

            for task in tasks:
                raw_dl = task.get("raw_deadline", "")
                task["deadline_iso"] = resolve_deadline_date(raw_dl, current_date)

            yield {
                "step": 3,
                "name": "Detecting deadlines",
                "status": "completed",
                "detail": f"Resolved hard deadlines for all {len(tasks)} tasks relative to {current_date}."
            }

            # Step 4: Calculating priorities
            yield {
                "step": 4,
                "name": "Calculating priorities",
                "status": "in_progress",
                "detail": "Evaluating urgency, effort, and deadline proximity..."
            }

            prioritized_tasks = calculate_priorities(tasks, current_date)
            workflow_results["prioritized_tasks"] = prioritized_tasks

            crit_count = sum(1 for t in prioritized_tasks if t.get("priority") == "CRITICAL")
            high_count = sum(1 for t in prioritized_tasks if t.get("priority") == "HIGH")

            yield {
                "step": 4,
                "name": "Calculating priorities",
                "status": "completed",
                "detail": f"Categorized priorities: {crit_count} CRITICAL, {high_count} HIGH, {len(prioritized_tasks)-crit_count-high_count} MEDIUM/LOW."
            }

            # Step 5: Breaking down tasks
            yield {
                "step": 5,
                "name": "Breaking down tasks",
                "status": "in_progress",
                "detail": "Decomposing complex tasks into practical subtasks (30m - 2h)..."
            }

            breakdown_prompt = BREAKDOWN_PROMPT_TEMPLATE.format(
                tasks_json=json.dumps(prioritized_tasks, indent=2)
            )
            raw_breakdown = self._call_gemini(breakdown_prompt)
            breakdown_data = clean_json_response(raw_breakdown)
            
            bd_map = {}
            for item in breakdown_data.get("task_breakdowns", []):
                t_id = item.get("task_id")
                subtasks = item.get("subtasks", [])
                bd_map[t_id] = subtasks

            for task in prioritized_tasks:
                t_id = task.get("id")
                if t_id not in bd_map or not bd_map[t_id]:
                    bd_map[t_id] = [{
                        "subtask_id": f"{t_id}_SUB_1",
                        "title": f"Execute {task.get('title')}",
                        "estimated_hours": task.get("estimated_hours", 2.0),
                        "order": 1
                    }]

            bd_map = ensure_dsa_subtasks(prioritized_tasks, bd_map)
            total_subtasks = sum(len(subs) for subs in bd_map.values())

            workflow_results["task_breakdowns"] = bd_map

            yield {
                "step": 5,
                "name": "Breaking down tasks",
                "status": "completed",
                "detail": f"Decomposed tasks into {total_subtasks} actionable subtasks (including Big-O, Trees, Graphs, DP, Mock Exam)."
            }

            # Step 6: Checking conflicts
            yield {
                "step": 6,
                "name": "Checking conflicts",
                "status": "in_progress",
                "detail": "Analyzing workload bottlenecks, daily caps, and deadline stacks..."
            }

            conflicts = detect_conflicts(prioritized_tasks, current_date, max_daily_hours)
            workflow_results["conflicts"] = conflicts

            yield {
                "step": 6,
                "name": "Checking conflicts",
                "status": "completed",
                "detail": f"Identified {len(conflicts)} potential scheduling conflict(s)."
            }

            # Step 7: Generating schedule
            yield {
                "step": 7,
                "name": "Generating schedule",
                "status": "in_progress",
                "detail": "Optimizing daily study allocations against strict event reservations and deadline cutoffs..."
            }

            tasks_with_subs = []
            for t in prioritized_tasks:
                t_copy = dict(t)
                t_copy["subtasks"] = bd_map.get(t.get("id"), [])
                tasks_with_subs.append(t_copy)

            scheduling_prompt = SCHEDULING_PROMPT_TEMPLATE.format(
                current_date=current_date,
                max_daily_hours=max_daily_hours,
                tasks_with_subtasks_json=json.dumps(tasks_with_subs, indent=2),
                conflicts_info_json=json.dumps(conflicts, indent=2)
            )

            raw_schedule = self._call_gemini(scheduling_prompt)
            schedule_data = clean_json_response(raw_schedule)

            schedule_data = audit_and_fix_schedule(
                schedule_data=schedule_data,
                prioritized_tasks=prioritized_tasks,
                reference_date=current_date,
                max_daily_hours=max_daily_hours
            )

            audit_conflicts = schedule_data.get("audit_conflicts", [])
            if audit_conflicts:
                conflicts.extend(audit_conflicts)
                workflow_results["conflicts"] = conflicts

            workflow_results["schedule"] = schedule_data

            val_results = validate_schedule(schedule_data, prioritized_tasks, current_date, max_daily_hours)
            workflow_results["validation"] = val_results

            yield {
                "step": 7,
                "name": "Generating schedule",
                "status": "completed",
                "detail": f"Generated study plan across {len(schedule_data.get('daily_schedule', []))} days (Validation score: {val_results.get('score')}/100)."
            }

            yield {
                "step": 8,
                "name": "Workflow Complete",
                "status": "finished",
                "detail": "Draft schedule generated and ready for human approval.",
                "results": workflow_results
            }

        except Exception as e:
            # Automatic graceful fallback to Local Demo Mode on any Gemini API quota/network error
            yield {
                "step": 2,
                "name": "Fallback to Demo Mode",
                "status": "warning",
                "detail": f"Gemini API issue ({str(e)}). Switching to Local Demo Mode."
            }

            demo_results = get_local_demo_results(current_date, max_daily_hours)

            for s_num in range(3, 8):
                yield {
                    "step": s_num,
                    "name": ["", "", "", "Detecting deadlines", "Calculating priorities", "Breaking down tasks", "Checking conflicts", "Generating schedule"][s_num],
                    "status": "completed",
                    "detail": f"[Demo Mode] Executed deterministic step {s_num} successfully."
                }

            yield {
                "step": 8,
                "name": "Workflow Complete",
                "status": "finished",
                "detail": "Fallback Demo Mode workflow completed successfully.",
                "results": demo_results
            }
