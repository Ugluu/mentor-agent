"""Command-line interface for the mentor agent."""

from __future__ import annotations

import argparse
import asyncio

from .agent import run_chat_session, run_query
from .memory import TaskStore


def cmd_brief(args: argparse.Namespace, store: TaskStore) -> None:
    prompt = (
        "Generate my morning briefing. Pull my current goals and open tasks, then give me "
        "a short prioritized plan for today: the one thing to do first and why, then the "
        "rest in priority order. Flag anything overdue or at risk."
    )
    result = asyncio.run(run_query(prompt, store, user_name=args.name))
    print(result)
    store.log_briefing(result)


def cmd_chat(args: argparse.Namespace, store: TaskStore) -> None:
    if args.message is None:
        asyncio.run(run_chat_session(store, user_name=args.name))
        return
    result = asyncio.run(run_query(args.message, store, user_name=args.name))
    print(result)


def cmd_add_goal(args: argparse.Namespace, store: TaskStore) -> None:
    goal = store.add_goal(title=args.title, category=args.category, target_date=args.due)
    print(f"Added goal [{goal.id}]: {goal.title}")


def cmd_add_task(args: argparse.Namespace, store: TaskStore) -> None:
    task = store.add_task(
        title=args.title, category=args.category, priority=args.priority, due_date=args.due
    )
    print(f"Added task [{task.id}]: {task.title}")


def cmd_tasks(args: argparse.Namespace, store: TaskStore) -> None:
    tasks = store.list_tasks(status="open")
    if not tasks:
        print("No open tasks.")
        return
    for t in tasks:
        due = f" (due {t['due_date']})" if t["due_date"] else ""
        print(f"[{t['id']}] P{t['priority']} {t['category']}: {t['title']}{due}")


def cmd_done(args: argparse.Namespace, store: TaskStore) -> None:
    ok = store.complete_task(args.task_id)
    print("Marked done." if ok else "No task with that id.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mentor", description="Your personal AI mentor.")
    parser.add_argument("--name", default="the user", help="Your name, used in the system prompt")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("brief", help="Generate today's prioritized morning briefing").set_defaults(
        func=cmd_brief
    )

    p_chat = sub.add_parser("chat", help="Ask your mentor something")
    p_chat.add_argument(
        "message", nargs="?", default=None,
        help="One-off question. Omit to start an interactive, multi-turn chat.",
    )
    p_chat.set_defaults(func=cmd_chat)

    p_goal = sub.add_parser("add-goal", help="Add a goal")
    p_goal.add_argument("title")
    p_goal.add_argument("--category", default="career", choices=["career", "business", "personal"])
    p_goal.add_argument("--due", default=None)
    p_goal.set_defaults(func=cmd_add_goal)

    p_task = sub.add_parser("add-task", help="Add a task")
    p_task.add_argument("title")
    p_task.add_argument("--category", default="career", choices=["career", "business", "personal"])
    p_task.add_argument("--priority", type=int, default=3, help="1 (highest) - 5 (lowest)")
    p_task.add_argument("--due", default=None)
    p_task.set_defaults(func=cmd_add_task)

    sub.add_parser("tasks", help="List open tasks").set_defaults(func=cmd_tasks)

    p_done = sub.add_parser("done", help="Mark a task complete")
    p_done.add_argument("task_id")
    p_done.set_defaults(func=cmd_done)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    store = TaskStore()
    args.func(args, store)


if __name__ == "__main__":
    main()
