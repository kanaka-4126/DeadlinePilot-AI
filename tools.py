"""
Utility functions, priority engines, conflict detection, schedule auditing, and validation tools for DeadlinePilot AI.
"""

from datetime import datetime, timedelta
import json
import re

SAMPLE_STUDENT_SCENARIO = """Hey DeadlinePilot! I'm completely overwhelmed with my computer science coursework this week. Here is everything on my plate:

1. Data Structures & Algorithms Midterm Exam: Worth 35% of my grade! The exam is in 2 days on Friday morning. Need to review Trees, Graphs, Dynamic Programming, and Big-O notation. Estimated study time: 8 hours total.
2. Operating Systems Lab Assignment 3: Implementing a virtual memory page replacement algorithm (LRU/FIFO) in C. Due in 3 days on Saturday at midnight. It's really complex and requires setup + coding + writing a test report. Estimated time: 6 hours.
3. Software Engineering Group Project Milestone: Need to finalize system architecture diagrams and deliver our API specification document. Group presentation is in 4 days on Sunday at 5 PM. Estimated effort: 4 hours.
4. Linear Algebra Problem Set 5: 10 vector space and matrix transformation problems. Due tomorrow (Thursday) at 11:59 PM. Estimated time: 3 hours.
5. Technical Writing Reading & Quiz: Read Chapters 4-5 on documentation best practices and take an online quiz. Quiz closes in 5 days (Monday). Estimated time: 1.5 hours.

Can you organize my schedule so I don't fail my midterm, get all assignments submitted on time, and avoid burning out?"""

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_date(date_str):
    """Safely parse ISO date string to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def resolve_deadline_date(raw_deadline, ref_date):
    """
    Consistently resolve relative date strings into concrete YYYY-MM-DD ISO strings.
    Handles weekday names ('friday morning', 'thursday 11:59 PM') and relative offsets.
    """
    ref_dt = parse_date(ref_date) if isinstance(ref_date, str) else ref_date
    if not ref_dt:
        ref_dt = datetime.now().date()

    raw_lower = str(raw_deadline or "").lower()

    for target_idx, day_name in enumerate(WEEKDAYS):
        if day_name in raw_lower:
            days_ahead = (target_idx - ref_dt.weekday()) % 7
            target_dt = ref_dt + timedelta(days=days_ahead)
            return target_dt.strftime("%Y-%m-%d")

    if "today" in raw_lower:
        return ref_dt.strftime("%Y-%m-%d")
    elif "tomorrow" in raw_lower:
        return (ref_dt + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "2 days" in raw_lower:
        return (ref_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    elif "3 days" in raw_lower:
        return (ref_dt + timedelta(days=3)).strftime("%Y-%m-%d")
    elif "4 days" in raw_lower:
        return (ref_dt + timedelta(days=4)).strftime("%Y-%m-%d")
    elif "5 days" in raw_lower:
        return (ref_dt + timedelta(days=5)).strftime("%Y-%m-%d")

    return (ref_dt + timedelta(days=1)).strftime("%Y-%m-%d")


def find_date_for_weekday(ref_dt, weekday_name):
    """Find the exact calendar date for a given weekday name on or after ref_dt."""
    target_idx = WEEKDAYS.index(weekday_name.lower())
    days_ahead = (target_idx - ref_dt.weekday()) % 7
    return ref_dt + timedelta(days=days_ahead)


def get_effective_deadline_cutoff(task, reference_date):
    """
    Determine the latest allowable date for scheduling work sessions for a task.
    If task is an exam or has a 'morning' deadline on date D, cutoff is D - 1.
    If task has an evening/midnight deadline on date D, cutoff is D.
    """
    ref_dt = parse_date(reference_date) if isinstance(reference_date, str) else reference_date
    if not ref_dt:
        ref_dt = datetime.now().date()

    raw_dl = str(task.get("raw_deadline", ""))
    deadline_iso = task.get("deadline_iso") or resolve_deadline_date(raw_dl, ref_dt)
    deadline_dt = parse_date(deadline_iso)
    if not deadline_dt:
        return ref_dt + timedelta(days=7)

    raw_lower = raw_dl.lower()
    task_type = str(task.get("task_type", "")).lower()

    if "exam" in task_type or "midterm" in task_type or "morning" in raw_lower:
        cutoff = deadline_dt - timedelta(days=1)
        if cutoff < ref_dt:
            cutoff = ref_dt
        return cutoff

    return deadline_dt


def ensure_dsa_subtasks(prioritized_tasks, bd_map):
    """
    Ensures that the Data Structures & Algorithms exam prep includes the 5 required topics:
    1. Big-O Notation & Complexity Analysis (1.5h)
    2. Trees & Binary Search Trees (1.5h)
    3. Graphs & Traversal Algorithms (BFS/DFS) (1.5h)
    4. Dynamic Programming Concepts (1.5h)
    5. Practice & Mock Midterm Exam (2.0h)
    """
    for task in prioritized_tasks:
        title_lower = str(task.get("title", "")).lower()
        if "data structure" in title_lower or "dsa" in title_lower or "midterm" in title_lower:
            t_id = task.get("id")
            if t_id:
                bd_map[t_id] = [
                    {"subtask_id": f"{t_id}_SUB_1", "title": "Big-O Notation & Complexity Analysis", "estimated_hours": 1.5, "order": 1},
                    {"subtask_id": f"{t_id}_SUB_2", "title": "Trees & Binary Search Trees", "estimated_hours": 1.5, "order": 2},
                    {"subtask_id": f"{t_id}_SUB_3", "title": "Graphs & Traversal Algorithms (BFS/DFS)", "estimated_hours": 1.5, "order": 3},
                    {"subtask_id": f"{t_id}_SUB_4", "title": "Dynamic Programming Concepts", "estimated_hours": 1.5, "order": 4},
                    {"subtask_id": f"{t_id}_SUB_5", "title": "Practice & Mock Midterm Exam", "estimated_hours": 2.0, "order": 5}
                ]
    return bd_map


def calculate_priorities(tasks, reference_date):
    """
    Calculate priority levels (CRITICAL, HIGH, MEDIUM, LOW) for each task based on
    deadline proximity, estimated hours, and task type.
    """
    ref_dt = parse_date(reference_date) if isinstance(reference_date, str) else reference_date
    if not ref_dt:
        ref_dt = datetime.now().date()

    prioritized_tasks = []
    for task in tasks:
        task_copy = dict(task)
        
        raw_dl = task.get("raw_deadline", "")
        task_copy["deadline_iso"] = resolve_deadline_date(raw_dl, ref_dt)
        deadline_dt = parse_date(task_copy["deadline_iso"])
        
        days_left = (deadline_dt - ref_dt).days if deadline_dt else 999
        est_hours = float(task.get("estimated_hours", 2.0))
        task_type = str(task.get("task_type", "")).lower()
        title_lower = str(task.get("title", "")).lower()

        score = 0
        if days_left <= 0:
            score += 120
        elif days_left <= 1:
            score += 100
        elif days_left <= 2:
            score += 80
        elif days_left <= 4:
            score += 50
        elif days_left <= 7:
            score += 25
        else:
            score += 10

        if "exam" in task_type or "midterm" in title_lower:
            score += 40
        elif "project" in task_type or "lab" in task_type:
            score += 20

        if est_hours >= 5.0:
            score += 15

        if score >= 90 or days_left <= 1:
            priority = "CRITICAL"
            badge_color = "red"
        elif score >= 60 or days_left <= 3:
            priority = "HIGH"
            badge_color = "orange"
        elif score >= 35 or days_left <= 7:
            priority = "MEDIUM"
            badge_color = "blue"
        else:
            priority = "LOW"
            badge_color = "green"

        task_copy["priority"] = priority
        task_copy["priority_score"] = score
        task_copy["days_left"] = days_left if days_left != 999 else "N/A"
        task_copy["badge_color"] = badge_color
        prioritized_tasks.append(task_copy)

    prioritized_tasks.sort(key=lambda x: x["priority_score"], reverse=True)
    return prioritized_tasks


def detect_conflicts(tasks, reference_date, max_daily_hours=6.0):
    """
    Detect scheduling conflicts, workload bottlenecks, and tight deadlines.
    """
    ref_dt = parse_date(reference_date) if isinstance(reference_date, str) else reference_date
    if not ref_dt:
        ref_dt = datetime.now().date()

    conflicts = []
    
    urgent_hours = 0.0
    critical_count = 0
    overdue_tasks = []

    for task in tasks:
        deadline_dt = parse_date(task.get("deadline_iso"))
        days_left = (deadline_dt - ref_dt).days if deadline_dt else 999
        est_hours = float(task.get("estimated_hours", 0.0))

        if days_left < 0:
            overdue_tasks.append(task.get("title"))
        elif days_left <= 2:
            urgent_hours += est_hours
            if task.get("priority") == "CRITICAL":
                critical_count += 1

    capacity_2d = max_daily_hours * 2
    if urgent_hours > capacity_2d:
        conflicts.append({
            "type": "WORKLOAD_OVERLOAD",
            "severity": "HIGH",
            "message": f"Workload Bottleneck: You have {urgent_hours:.1f} hours of work due in the next 48 hours, but your total capacity is {capacity_2d:.1f} hours ({max_daily_hours}h/day)."
        })

    if critical_count >= 2:
        conflicts.append({
            "type": "CRITICAL_STACK",
            "severity": "HIGH",
            "message": f"Deadline Stacking: {critical_count} critical deadlines occurring within 24-48 hours."
        })

    if overdue_tasks:
        conflicts.append({
            "type": "OVERDUE_TASK",
            "severity": "MEDIUM",
            "message": f"Passed/Today Deadlines detected for: {', '.join(overdue_tasks)}."
        })

    return conflicts


def audit_and_fix_schedule(schedule_data, prioritized_tasks, reference_date, max_daily_hours=6.0):
    """
    Enforces strict calendar date resolution, event reservations, OS Lab sequencing, and capacity caps.
    - Friday Morning (2026-10-09) reserved for DSA Midterm Exam.
    - DSA Prep completed strictly BEFORE Friday morning.
    - Linear Algebra completed Thursday 2026-10-08 by 11:59 PM.
    - OS Lab work scheduled AFTER Friday morning DSA exam and completed by Saturday 2026-10-10 midnight.
    - Software Engineering completed before Sunday 2026-10-11 at 5 PM.
    - Technical Writing deferred to Sunday/Monday.
    """
    ref_dt = parse_date(reference_date) if isinstance(reference_date, str) else reference_date
    if not ref_dt:
        ref_dt = datetime.now().date()

    thu_dt = find_date_for_weekday(ref_dt, "thursday")
    fri_dt = find_date_for_weekday(ref_dt, "friday")
    sat_dt = find_date_for_weekday(ref_dt, "saturday")
    sun_dt = find_date_for_weekday(ref_dt, "sunday")
    mon_dt = find_date_for_weekday(ref_dt, "monday")

    cutoff_map = {}
    dsa_task_id = None
    os_task_id = None
    tech_writing_id = None

    for task in prioritized_tasks:
        t_id = task.get("id")
        title_lower = str(task.get("title", "")).lower()
        if t_id:
            cutoff_map[t_id] = get_effective_deadline_cutoff(task, ref_dt)
            if "data structure" in title_lower or "dsa" in title_lower or "midterm" in title_lower:
                dsa_task_id = t_id
            elif "operating system" in title_lower or "os lab" in title_lower or "lab" in title_lower:
                os_task_id = t_id
            elif "technical writing" in title_lower or "writing" in title_lower or "quiz" in title_lower:
                tech_writing_id = t_id

    if not isinstance(schedule_data, dict):
        schedule_data = {"daily_schedule": [], "unassigned_tasks": []}

    daily_schedule = schedule_data.get("daily_schedule", [])
    unassigned_tasks = schedule_data.get("unassigned_tasks", [])
    if not isinstance(unassigned_tasks, list):
        unassigned_tasks = []

    capacity_conflicts = []

    fri_str = fri_dt.strftime("%Y-%m-%d")
    fri_day_entry = next((d for d in daily_schedule if d.get("date") == fri_str), None)
    if not fri_day_entry:
        fri_day_entry = {
            "date": fri_str,
            "day_name": fri_dt.strftime("%A"),
            "total_hours": 0.0,
            "items": []
        }
        daily_schedule.append(fri_day_entry)

    has_event_marker = any("RESERVED EVENT" in item.get("title", "") for item in fri_day_entry.get("items", []))
    if not has_event_marker:
        fri_day_entry["items"].insert(0, {
            "task_id": dsa_task_id or "RESERVED_EXAM",
            "subtask_id": "RESERVED_EXAM_BLOCK",
            "title": "⛔ [RESERVED EVENT] Data Structures Midterm Exam",
            "duration_hours": 0.0,
            "time_block": "Morning",
            "focus_note": "Actual exam time - no study sessions allowed during/after exam"
        })

    day_hours_map = {}
    for day in daily_schedule:
        d_str = day.get("date")
        if d_str:
            day_hours_map[d_str] = sum(float(i.get("duration_hours", 0.0)) for i in day.get("items", []))

    cleaned_daily_schedule = []

    for day in daily_schedule:
        day_date = parse_date(day.get("date"))
        if not day_date:
            cleaned_daily_schedule.append(day)
            continue

        valid_items = []
        for item in day.get("items", []):
            t_id = item.get("task_id")
            item_duration = float(item.get("duration_hours", 0.0))
            task_title = item.get("title", "Task")

            if "RESERVED EVENT" in task_title:
                valid_items.append(item)
                continue

            cutoff = cutoff_map.get(t_id)

            if t_id == dsa_task_id and day_date >= fri_dt:
                relocated = False
                for try_dt in [thu_dt, ref_dt]:
                    c_str = try_dt.strftime("%Y-%m-%d")
                    if day_hours_map.get(c_str, 0.0) + item_duration <= max_daily_hours + 0.5:
                        day_target = next((d for d in cleaned_daily_schedule if d.get("date") == c_str), None)
                        if not day_target:
                            day_target = {"date": c_str, "day_name": try_dt.strftime("%A"), "total_hours": 0.0, "items": []}
                            cleaned_daily_schedule.append(day_target)
                        item["focus_note"] = f"(Scheduled before Friday morning exam) {item.get('focus_note', '')}"
                        day_target["items"].append(item)
                        day_target["total_hours"] = round(day_target["total_hours"] + item_duration, 1)
                        day_hours_map[c_str] = day_target["total_hours"]
                        relocated = True
                        break

                if not relocated:
                    unassigned_tasks.append({
                        "task_id": t_id,
                        "title": task_title,
                        "duration_hours": item_duration,
                        "reason": f"Deadline Conflict: Cannot fit {item_duration}h of DSA prep before Friday 2026-10-09 morning exam due to daily capacity limit ({max_daily_hours}h/day).",
                        "deferral_recommendation": "Increase daily study capacity slider or defer lower-priority work to free capacity."
                    })
                    capacity_conflicts.append({
                        "type": "EXAM_PREP_OVERFLOW",
                        "severity": "HIGH",
                        "message": f"Exam Capacity Limit: '{task_title}' ({item_duration}h) could not fit before Friday morning exam."
                    })
                continue

            if t_id == os_task_id and day_date < fri_dt:
                relocated = False
                for try_dt in [fri_dt, sat_dt]:
                    c_str = try_dt.strftime("%Y-%m-%d")
                    if day_hours_map.get(c_str, 0.0) + item_duration <= max_daily_hours + 0.5:
                        day_target = next((d for d in cleaned_daily_schedule if d.get("date") == c_str), None)
                        if not day_target:
                            day_target = {"date": c_str, "day_name": try_dt.strftime("%A"), "total_hours": 0.0, "items": []}
                            cleaned_daily_schedule.append(day_target)
                        item["time_block"] = "Afternoon / Evening" if try_dt == fri_dt else item.get("time_block", "Afternoon")
                        item["focus_note"] = f"(Scheduled after DSA exam) {item.get('focus_note', '')}"
                        day_target["items"].append(item)
                        day_target["total_hours"] = round(day_target["total_hours"] + item_duration, 1)
                        day_hours_map[c_str] = day_target["total_hours"]
                        relocated = True
                        break

                if not relocated:
                    valid_items.append(item)
                continue

            if t_id == tech_writing_id and day_date < sun_dt:
                relocated = False
                for try_dt in [sun_dt, mon_dt]:
                    c_str = try_dt.strftime("%Y-%m-%d")
                    if day_hours_map.get(c_str, 0.0) + item_duration <= max_daily_hours + 0.5:
                        day_target = next((d for d in cleaned_daily_schedule if d.get("date") == c_str), None)
                        if not day_target:
                            day_target = {"date": c_str, "day_name": try_dt.strftime("%A"), "total_hours": 0.0, "items": []}
                            cleaned_daily_schedule.append(day_target)
                        item["focus_note"] = f"(Deferred after urgent CS deadlines) {item.get('focus_note', '')}"
                        day_target["items"].append(item)
                        day_target["total_hours"] = round(day_target["total_hours"] + item_duration, 1)
                        day_hours_map[c_str] = day_target["total_hours"]
                        relocated = True
                        break

                if not relocated:
                    valid_items.append(item)
                continue

            if cutoff and day_date > cutoff:
                relocated = False
                curr_check = cutoff
                while curr_check >= ref_dt:
                    c_str = curr_check.strftime("%Y-%m-%d")
                    if day_hours_map.get(c_str, 0.0) + item_duration <= max_daily_hours + 0.5:
                        day_target = next((d for d in cleaned_daily_schedule if d.get("date") == c_str), None)
                        if not day_target:
                            day_target = {"date": c_str, "day_name": curr_check.strftime("%A"), "total_hours": 0.0, "items": []}
                            cleaned_daily_schedule.append(day_target)
                        day_target["items"].append(item)
                        day_target["total_hours"] = round(day_target["total_hours"] + item_duration, 1)
                        day_hours_map[c_str] = day_target["total_hours"]
                        relocated = True
                        break
                    curr_check -= timedelta(days=1)

                if not relocated:
                    unassigned_tasks.append({
                        "task_id": t_id,
                        "title": task_title,
                        "duration_hours": item_duration,
                        "reason": f"Capacity Conflict: Cannot fit {item_duration}h for '{task_title}' before deadline cutoff {cutoff.strftime('%Y-%m-%d')}.",
                        "deferral_recommendation": "Defer non-critical tasks to later days."
                    })
                    capacity_conflicts.append({
                        "type": "DEADLINE_CAPACITY_OVERFLOW",
                        "severity": "HIGH",
                        "message": f"Capacity Overload: Session '{task_title}' ({item_duration}h) could not fit before hard deadline cutoff {cutoff.strftime('%Y-%m-%d')}."
                    })
            else:
                valid_items.append(item)

        day["items"] = valid_items
        day["total_hours"] = round(sum(float(i.get("duration_hours", 0.0)) for i in valid_items), 1)
        if valid_items or day.get("date"):
            cleaned_daily_schedule.append(day)

    cleaned_daily_schedule.sort(key=lambda d: d.get("date", ""))

    schedule_data["daily_schedule"] = cleaned_daily_schedule
    schedule_data["unassigned_tasks"] = unassigned_tasks
    schedule_data["audit_conflicts"] = capacity_conflicts

    return schedule_data


def validate_schedule(schedule_data, tasks, reference_date, max_daily_hours=6.0):
    """
    Validate generated schedule against constraints:
    - Missed deadlines (working on task after deadline cutoff)
    - Overloaded days (daily hours > max capacity)
    - Unrealistic durations
    - Missing / unassigned tasks
    """
    ref_dt = parse_date(reference_date) if isinstance(reference_date, str) else reference_date
    if not ref_dt:
        ref_dt = datetime.now().date()

    task_cutoff_map = {}
    for task in tasks:
        t_id = task.get("id")
        cutoff = get_effective_deadline_cutoff(task, ref_dt)
        if t_id and cutoff:
            task_cutoff_map[t_id] = cutoff

    warnings = []
    daily_schedules = schedule_data.get("daily_schedule", []) if isinstance(schedule_data, dict) else []

    scheduled_task_ids = set()

    for day in daily_schedules:
        day_date = parse_date(day.get("date"))
        day_total_hours = float(day.get("total_hours", 0.0))

        if day_total_hours > max_daily_hours + 0.5:
            warnings.append(f"Day {day.get('date')} ({day.get('day_name')}) is overloaded: {day_total_hours:.1f} hours scheduled (Limit: {max_daily_hours}h).")

        for item in day.get("items", []):
            t_id = item.get("task_id")
            if t_id:
                scheduled_task_ids.add(t_id)
                cutoff = task_cutoff_map.get(t_id)
                if cutoff and day_date and day_date > cutoff and "RESERVED EVENT" not in item.get("title", ""):
                    warnings.append(f"VIOLATION: Task '{item.get('title')}' scheduled on {day_date} which is AFTER its deadline cutoff {cutoff}!")

    unassigned = schedule_data.get("unassigned_tasks", []) if isinstance(schedule_data, dict) else []
    if unassigned:
        for u in unassigned:
            warnings.append(f"Capacity Bottleneck: '{u.get('title')}' could not be fully scheduled before deadline ({u.get('reason', '')}).")

    is_valid = len(warnings) == 0
    validation_score = max(0, 100 - (len(warnings) * 15))

    return {
        "valid": is_valid,
        "score": validation_score,
        "warnings": warnings
    }


def clean_json_response(raw_response_text):
    """
    Clean raw model output string to extract clean JSON object/array.
    Strips markdown code blocks ```json ... ```.
    """
    if not raw_response_text:
        return {}
    
    text = raw_response_text.strip()
    
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return {}


def get_local_demo_results(current_date, max_daily_hours=6.0):
    """
    Generates deterministic, local Demo Mode data structures matching exact dates:
    Reference Date: current_date (Thursday 2026-10-08)
    - DSA Exam: Friday 2026-10-09 Morning
    - Linear Algebra: Thursday 2026-10-08 11:59 PM
    - OS Lab: Saturday 2026-10-10 Midnight
    - SE Project: Sunday 2026-10-11 5 PM
    - Technical Writing: Monday 2026-10-12
    """
    ref_dt = parse_date(current_date) if isinstance(current_date, str) else current_date
    if not ref_dt:
        ref_dt = datetime.now().date()

    thu_dt = find_date_for_weekday(ref_dt, "thursday")
    fri_dt = find_date_for_weekday(ref_dt, "friday")
    sat_dt = find_date_for_weekday(ref_dt, "saturday")
    sun_dt = find_date_for_weekday(ref_dt, "sunday")
    mon_dt = find_date_for_weekday(ref_dt, "monday")

    thu_str = thu_dt.strftime("%Y-%m-%d")
    fri_str = fri_dt.strftime("%Y-%m-%d")
    sat_str = sat_dt.strftime("%Y-%m-%d")
    sun_str = sun_dt.strftime("%Y-%m-%d")
    mon_str = mon_dt.strftime("%Y-%m-%d")

    tasks = [
        {
            "id": "TASK_1",
            "title": "Data Structures & Algorithms Midterm Exam",
            "task_type": "exam",
            "description": "Midterm exam worth 35% of grade covering Trees, Graphs, DP, and Big-O",
            "raw_deadline": "Friday morning",
            "deadline_iso": fri_str,
            "estimated_hours": 8.0,
            "urgency_notes": "High stakes 35% midterm exam",
            "dependencies": []
        },
        {
            "id": "TASK_2",
            "title": "Linear Algebra Problem Set 5",
            "task_type": "assignment",
            "description": "10 vector space and matrix transformation problems",
            "raw_deadline": "Thursday at 11:59 PM",
            "deadline_iso": thu_str,
            "estimated_hours": 3.0,
            "urgency_notes": "Due tonight at 11:59 PM",
            "dependencies": []
        },
        {
            "id": "TASK_3",
            "title": "Operating Systems Lab Assignment 3",
            "task_type": "lab",
            "description": "Virtual memory page replacement algorithm (LRU/FIFO) in C",
            "raw_deadline": "Saturday at midnight",
            "deadline_iso": sat_str,
            "estimated_hours": 6.0,
            "urgency_notes": "Complex C coding + test report",
            "dependencies": ["TASK_1"]
        },
        {
            "id": "TASK_4",
            "title": "Software Engineering Group Project Milestone",
            "task_type": "project",
            "description": "Finalize system architecture diagrams and API spec document",
            "raw_deadline": "Sunday at 5 PM",
            "deadline_iso": sun_str,
            "estimated_hours": 4.0,
            "urgency_notes": "Group presentation & milestone submission",
            "dependencies": []
        },
        {
            "id": "TASK_5",
            "title": "Technical Writing Reading & Quiz",
            "task_type": "reading",
            "description": "Read Chapters 4-5 documentation best practices and take online quiz",
            "raw_deadline": "Monday",
            "deadline_iso": mon_str,
            "estimated_hours": 1.5,
            "urgency_notes": "Quiz closes Monday",
            "dependencies": []
        }
    ]

    prioritized = calculate_priorities(tasks, ref_dt)
    
    bd_map = {
        "TASK_1": [
            {"subtask_id": "TASK_1_SUB_1", "title": "Big-O Notation & Complexity Analysis", "estimated_hours": 1.5, "order": 1},
            {"subtask_id": "TASK_1_SUB_2", "title": "Trees & Binary Search Trees", "estimated_hours": 1.5, "order": 2},
            {"subtask_id": "TASK_1_SUB_3", "title": "Graphs & Traversal Algorithms (BFS/DFS)", "estimated_hours": 1.5, "order": 3},
            {"subtask_id": "TASK_1_SUB_4", "title": "Dynamic Programming Concepts", "estimated_hours": 1.5, "order": 4},
            {"subtask_id": "TASK_1_SUB_5", "title": "Practice & Mock Midterm Exam", "estimated_hours": 2.0, "order": 5}
        ],
        "TASK_2": [
            {"subtask_id": "TASK_2_SUB_1", "title": "Vector Spaces & Matrix Transformations", "estimated_hours": 3.0, "order": 1}
        ],
        "TASK_3": [
            {"subtask_id": "TASK_3_SUB_1", "title": "LRU/FIFO Page Replacement Setup & C Coding", "estimated_hours": 3.0, "order": 1},
            {"subtask_id": "TASK_3_SUB_2", "title": "Testing & Virtual Memory Lab Report", "estimated_hours": 3.0, "order": 2}
        ],
        "TASK_4": [
            {"subtask_id": "TASK_4_SUB_1", "title": "System Architecture Diagrams", "estimated_hours": 2.0, "order": 1},
            {"subtask_id": "TASK_4_SUB_2", "title": "API Spec Document & Group Deck", "estimated_hours": 2.0, "order": 2}
        ],
        "TASK_5": [
            {"subtask_id": "TASK_5_SUB_1", "title": "Read Chapters 4-5 & Take Online Quiz", "estimated_hours": 1.5, "order": 1}
        ]
    }

    conflicts = detect_conflicts(prioritized, ref_dt, max_daily_hours)

    # Build deterministic daily schedule respecting capacity cap & cutoffs
    daily_schedule = []

    # Thursday (2026-10-08)
    daily_schedule.append({
        "date": thu_str,
        "day_name": thu_dt.strftime("%A"),
        "total_hours": 6.0,
        "items": [
            {"task_id": "TASK_2", "subtask_id": "TASK_2_SUB_1", "title": "Linear Algebra: Vector Spaces & Matrix Transformations", "duration_hours": 3.0, "time_block": "Morning", "focus_note": "Finish before 11:59 PM deadline tonight"},
            {"task_id": "TASK_1", "subtask_id": "TASK_1_SUB_1", "title": "DSA Exam Prep: Big-O Notation & Complexity Analysis", "duration_hours": 1.5, "time_block": "Afternoon", "focus_note": "Core runtime analysis concepts"},
            {"task_id": "TASK_1", "subtask_id": "TASK_1_SUB_2", "title": "DSA Exam Prep: Trees & Binary Search Trees", "duration_hours": 1.5, "time_block": "Evening", "focus_note": "Tree traversals & balancing"}
        ]
    })

    # Friday (2026-10-09)
    daily_schedule.append({
        "date": fri_str,
        "day_name": fri_dt.strftime("%A"),
        "total_hours": 6.0,
        "items": [
            {"task_id": "TASK_1", "subtask_id": "RESERVED_EXAM_BLOCK", "title": "⛔ [RESERVED EVENT] Data Structures Midterm Exam", "duration_hours": 0.0, "time_block": "Morning", "focus_note": "Actual exam time - no study sessions allowed during/after exam"},
            {"task_id": "TASK_3", "subtask_id": "TASK_3_SUB_1", "title": "OS Lab 3: LRU/FIFO Page Replacement Setup & C Coding", "duration_hours": 3.0, "time_block": "Afternoon", "focus_note": "Scheduled after DSA exam"},
            {"task_id": "TASK_3", "subtask_id": "TASK_3_SUB_2", "title": "OS Lab 3: Testing & Virtual Memory Lab Report", "duration_hours": 3.0, "time_block": "Evening", "focus_note": "Complete before Saturday midnight"}
        ]
    })

    # Saturday (2026-10-10)
    daily_schedule.append({
        "date": sat_str,
        "day_name": sat_dt.strftime("%A"),
        "total_hours": 4.0,
        "items": [
            {"task_id": "TASK_4", "subtask_id": "TASK_4_SUB_1", "title": "Software Engineering: System Architecture Diagrams", "duration_hours": 2.0, "time_block": "Morning", "focus_note": "Component & sequence diagrams"},
            {"task_id": "TASK_4", "subtask_id": "TASK_4_SUB_2", "title": "Software Engineering: API Spec Document & Group Deck", "duration_hours": 2.0, "time_block": "Afternoon", "focus_note": "Prepare for Sunday 5 PM presentation"}
        ]
    })

    # Sunday (2026-10-11)
    daily_schedule.append({
        "date": sun_str,
        "day_name": sun_dt.strftime("%A"),
        "total_hours": 1.5,
        "items": [
            {"task_id": "TASK_5", "subtask_id": "TASK_5_SUB_1", "title": "Technical Writing: Read Chapters 4-5 & Take Online Quiz", "duration_hours": 1.5, "time_block": "Afternoon", "focus_note": "Deferred after urgent CS deadlines"}
        ]
    })

    # Handle unassigned overflow if max capacity on Thursday is 6.0h (5.0h DSA prep overflow)
    unassigned_tasks = []
    if max_daily_hours < 11.0:
        unassigned_tasks.append({
            "task_id": "TASK_1",
            "title": "DSA Exam Prep: Graphs, Dynamic Programming & Mock Exam",
            "duration_hours": 5.0,
            "reason": f"Capacity Bottleneck: Cannot fit remaining 5.0h of DSA prep on Thursday {thu_str} before Friday morning exam due to daily limit ({max_daily_hours}h/day cap).",
            "deferral_recommendation": "To complete all 8.0h of DSA prep before Friday morning, increase daily study capacity slider to 11.0h on Thursday."
        })
        conflicts.append({
            "type": "DEADLINE_CAPACITY_OVERFLOW",
            "severity": "HIGH",
            "message": f"Capacity Limit: 5.0h of DSA prep could not fit on Thursday {thu_str} before Friday morning exam within {max_daily_hours}h/day cap."
        })

    schedule_data = {
        "schedule_strategy": "Date-Aligned Local Demo Strategy: DSA prep strictly prior to Friday exam, OS Lab post-exam, SE pre-Sunday, and Tech Writing deferred.",
        "daily_schedule": daily_schedule,
        "unassigned_tasks": unassigned_tasks,
        "audit_conflicts": []
    }

    val_results = validate_schedule(schedule_data, prioritized, ref_dt, max_daily_hours)

    return {
        "is_demo_mode": True,
        "summary": f"Built-in Local Demo Mode: Analyzed 5 CS student commitments relative to {current_date}.",
        "tasks": tasks,
        "prioritized_tasks": prioritized,
        "task_breakdowns": bd_map,
        "conflicts": conflicts,
        "schedule": schedule_data,
        "validation": val_results
    }
