
import unittest
from tools import (
    calculate_priorities,
    detect_conflicts,
    ensure_dsa_subtasks,
    clean_json_response,
    validate_schedule,
)


class TestDeadlinePilotTools(unittest.TestCase):

    def test_urgent_task_is_critical(self):
        tasks = [{
            "id": "T1",
            "title": "Assignment",
            "task_type": "assignment",
            "raw_deadline": "2026-10-10",
            "estimated_hours": 2
        }]
        result = calculate_priorities(tasks, "2026-10-09")
        self.assertEqual(result[0]["priority"], "CRITICAL")

    def test_workload_overload_is_detected(self):
        tasks = [
            {
                "title": "Task A",
                "deadline_iso": "2026-10-10",
                "estimated_hours": 7,
                "priority": "CRITICAL"
            },
            {
                "title": "Task B",
                "deadline_iso": "2026-10-10",
                "estimated_hours": 7,
                "priority": "CRITICAL"
            }
        ]
        result = detect_conflicts(
            tasks, "2026-10-09", max_daily_hours=6
        )
        conflict_types = {item["type"] for item in result}
        self.assertIn("WORKLOAD_OVERLOAD", conflict_types)
        self.assertIn("CRITICAL_STACK", conflict_types)

    def test_dsa_topics_are_created(self):
        tasks = [{"id": "T1", "title": "DSA Midterm"}]
        result = ensure_dsa_subtasks(tasks, {})
        self.assertEqual(len(result["T1"]), 5)

    def test_valid_json_is_parsed(self):
        result = clean_json_response('{"tasks": []}')
        self.assertEqual(result, {"tasks": []})

    def test_markdown_json_is_parsed(self):
        result = clean_json_response(
            '```json\n{"tasks": []}\n```'
        )
        self.assertEqual(result, {"tasks": []})

    def test_invalid_json_returns_empty_object(self):
        result = clean_json_response("not valid json")
        self.assertEqual(result, {})

    def test_schedule_deadline_violation_is_reported(self):
        tasks = [{
            "id": "T1",
            "title": "Assignment",
            "task_type": "assignment",
            "raw_deadline": "2026-10-10",
            "deadline_iso": "2026-10-10"
        }]
        schedule = {
            "daily_schedule": [{
                "date": "2026-10-11",
                "day_name": "Sunday",
                "total_hours": 2,
                "items": [{
                    "task_id": "T1",
                    "title": "Assignment",
                    "duration_hours": 2
                }]
            }],
            "unassigned_tasks": []
        }
        result = validate_schedule(
            schedule, tasks, "2026-10-09"
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
import unittest
from tools import (
    calculate_priorities,
    detect_conflicts,
    ensure_dsa_subtasks,
    clean_json_response,
    validate_schedule,
)


class TestDeadlinePilotTools(unittest.TestCase):

    def test_urgent_task_is_critical(self):
        tasks = [{
            "id": "T1",
            "title": "Assignment",
            "task_type": "assignment",
            "raw_deadline": "2026-10-10",
            "estimated_hours": 2
        }]
        result = calculate_priorities(tasks, "2026-10-09")
        self.assertEqual(result[0]["priority"], "CRITICAL")

    def test_workload_overload_is_detected(self):
        tasks = [
            {
                "title": "Task A",
                "deadline_iso": "2026-10-10",
                "estimated_hours": 7,
                "priority": "CRITICAL"
            },
            {
                "title": "Task B",
                "deadline_iso": "2026-10-10",
                "estimated_hours": 7,
                "priority": "CRITICAL"
            }
        ]
        result = detect_conflicts(
            tasks, "2026-10-09", max_daily_hours=6
        )
        conflict_types = {item["type"] for item in result}
        self.assertIn("WORKLOAD_OVERLOAD", conflict_types)
        self.assertIn("CRITICAL_STACK", conflict_types)

    def test_dsa_topics_are_created(self):
        tasks = [{"id": "T1", "title": "DSA Midterm"}]
        result = ensure_dsa_subtasks(tasks, {})
        self.assertEqual(len(result["T1"]), 5)

    def test_valid_json_is_parsed(self):
        result = clean_json_response('{"tasks": []}')
        self.assertEqual(result, {"tasks": []})

    def test_markdown_json_is_parsed(self):
        result = clean_json_response(
            '```json\n{"tasks": []}\n```'
        )
        self.assertEqual(result, {"tasks": []})

    def test_invalid_json_returns_empty_object(self):
        result = clean_json_response("not valid json")
        self.assertEqual(result, {})

    def test_schedule_deadline_violation_is_reported(self):
        tasks = [{
            "id": "T1",
            "title": "Assignment",
            "task_type": "assignment",
            "raw_deadline": "2026-10-10",
            "deadline_iso": "2026-10-10"
        }]
        schedule = {
            "daily_schedule": [{
                "date": "2026-10-11",
                "day_name": "Sunday",
                "total_hours": 2,
                "items": [{
                    "task_id": "T1",
                    "title": "Assignment",
                    "duration_hours": 2
                }]
            }],
            "unassigned_tasks": []
        }
        result = validate_schedule(
            schedule, tasks, "2026-10-09"
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main(verbosity=2)