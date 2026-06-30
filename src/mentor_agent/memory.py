"""Persistent storage for goals, tasks, and past briefings."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, date
from pathlib import Path


def _default_data_path() -> Path:
    home = os.environ.get("MENTOR_AGENT_HOME", str(Path.home() / ".mentor_agent"))
    return Path(home) / "data.json"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Goal:
    id: str
    title: str
    category: str  # career | business | personal
    target_date: str | None = None
    status: str = "active"  # active | done | dropped
    created_at: str = field(default_factory=_now)
    notes: str = ""


@dataclass
class Task:
    id: str
    title: str
    category: str  # career | business | personal
    priority: int = 3  # 1 (highest) - 5 (lowest)
    due_date: str | None = None
    status: str = "open"  # open | done
    created_at: str = field(default_factory=_now)
    completed_at: str | None = None
    notes: str = ""


class TaskStore:
    """JSON-backed store for a single user's goals, tasks, and briefing history."""

    def __init__(self, path: Path | None = None):
        self.path = path or _default_data_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r") as f:
                return json.load(f)
        return {"goals": [], "tasks": [], "briefings": []}

    def _save(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    # -- goals --------------------------------------------------------

    def add_goal(self, title: str, category: str, target_date: str | None = None, notes: str = "") -> Goal:
        goal = Goal(id=str(uuid.uuid4())[:8], title=title, category=category, target_date=target_date, notes=notes)
        self._data["goals"].append(asdict(goal))
        self._save()
        return goal

    def list_goals(self, status: str | None = "active") -> list[dict]:
        goals = self._data["goals"]
        if status:
            goals = [g for g in goals if g["status"] == status]
        return goals

    # -- tasks --------------------------------------------------------

    def add_task(
        self,
        title: str,
        category: str,
        priority: int = 3,
        due_date: str | None = None,
        notes: str = "",
    ) -> Task:
        task = Task(
            id=str(uuid.uuid4())[:8],
            title=title,
            category=category,
            priority=priority,
            due_date=due_date,
            notes=notes,
        )
        self._data["tasks"].append(asdict(task))
        self._save()
        return task

    def list_tasks(self, status: str | None = "open") -> list[dict]:
        tasks = self._data["tasks"]
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return sorted(tasks, key=lambda t: (t["priority"], t.get("due_date") or "9999-99-99"))

    def complete_task(self, task_id: str) -> bool:
        for t in self._data["tasks"]:
            if t["id"] == task_id:
                t["status"] = "done"
                t["completed_at"] = _now()
                self._save()
                return True
        return False

    # -- briefings ------------------------------------------------------

    def log_briefing(self, summary: str) -> None:
        self._data["briefings"].append({"date": date.today().isoformat(), "summary": summary})
        self._save()

    def recent_briefings(self, limit: int = 5) -> list[dict]:
        return self._data["briefings"][-limit:]
