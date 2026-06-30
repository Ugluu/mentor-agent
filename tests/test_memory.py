from pathlib import Path

from mentor_agent.memory import TaskStore


def make_store(tmp_path: Path) -> TaskStore:
    return TaskStore(path=tmp_path / "data.json")


def test_add_and_list_task(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_task("Ship pitch deck", category="business", priority=1)
    tasks = store.list_tasks(status="open")
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Ship pitch deck"
    assert tasks[0]["priority"] == 1


def test_tasks_sorted_by_priority(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add_task("Low priority", category="personal", priority=5)
    store.add_task("High priority", category="career", priority=1)
    tasks = store.list_tasks(status="open")
    assert [t["title"] for t in tasks] == ["High priority", "Low priority"]


def test_complete_task(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    task = store.add_task("Follow up with recruiter", category="career")
    assert store.complete_task(task.id) is True
    assert store.list_tasks(status="open") == []
    done = store.list_tasks(status="done")
    assert len(done) == 1
    assert done[0]["completed_at"] is not None


def test_complete_unknown_task_returns_false(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    assert store.complete_task("doesnotexist") is False


def test_goals_and_persistence(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    store = TaskStore(path=path)
    store.add_goal("Launch business in London", category="business")

    # Reload from disk to confirm persistence
    reloaded = TaskStore(path=path)
    goals = reloaded.list_goals(status="active")
    assert len(goals) == 1
    assert goals[0]["title"] == "Launch business in London"


def test_log_and_recent_briefings(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.log_briefing("Today: ship the deck first.")
    briefings = store.recent_briefings()
    assert len(briefings) == 1
    assert "ship the deck" in briefings[0]["summary"]
