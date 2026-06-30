"""Claude Agent SDK wiring: tools, system prompt, and the query entrypoint."""

from __future__ import annotations

from datetime import date
from typing import Any

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

from .memory import TaskStore

SYSTEM_PROMPT = """You are {name}'s personal mentor: a direct, knowledgeable advisor on \
career and business strategy. {name} is based in London, working on advancing their career \
and getting a business off the ground. Your job is to:

- Turn their goals and open tasks into a clear, prioritized plan.
- Always lead with the single most important thing to do today, and say why.
- Push back when priorities are vague, avoidant, or there are too many "P1"s to be real.
- Be concise and concrete. No filler, no generic motivational language.

Today is {today}. Always use the available tools to read (and, when asked, update) their \
goals and task list before giving advice — never guess at what's on their plate.
"""


def build_tools(store: TaskStore) -> list:
    @tool("list_tasks", "List the user's open tasks, sorted by priority", {})
    async def list_tasks(args: dict[str, Any]) -> dict[str, Any]:
        tasks = store.list_tasks(status="open")
        if not tasks:
            text = "No open tasks."
        else:
            text = "\n".join(
                f"- [{t['id']}] (P{t['priority']}, {t['category']}"
                f"{', due ' + t['due_date'] if t['due_date'] else ''}) {t['title']}"
                for t in tasks
            )
        return {"content": [{"type": "text", "text": text}]}

    @tool("list_goals", "List the user's active goals", {})
    async def list_goals(args: dict[str, Any]) -> dict[str, Any]:
        goals = store.list_goals(status="active")
        if not goals:
            text = "No active goals set."
        else:
            text = "\n".join(f"- [{g['category']}] {g['title']}" for g in goals)
        return {"content": [{"type": "text", "text": text}]}

    @tool(
        "add_task",
        "Add a new task to the user's task list",
        {"title": str, "category": str, "priority": int, "due_date": str},
    )
    async def add_task(args: dict[str, Any]) -> dict[str, Any]:
        task = store.add_task(
            title=args["title"],
            category=args.get("category", "career"),
            priority=int(args.get("priority", 3)),
            due_date=args.get("due_date") or None,
        )
        return {"content": [{"type": "text", "text": f"Added task [{task.id}]: {task.title}"}]}

    @tool("complete_task", "Mark a task as done by its id", {"task_id": str})
    async def complete_task(args: dict[str, Any]) -> dict[str, Any]:
        ok = store.complete_task(args["task_id"])
        text = "Marked done." if ok else "No task with that id."
        return {"content": [{"type": "text", "text": text}]}

    return [list_tasks, list_goals, add_task, complete_task]


def build_options(store: TaskStore, user_name: str = "the user") -> ClaudeAgentOptions:
    server = create_sdk_mcp_server(name="mentor", version="1.0.0", tools=build_tools(store))
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT.format(name=user_name, today=date.today().isoformat()),
        mcp_servers={"mentor": server},
        allowed_tools=[
            "mcp__mentor__list_tasks",
            "mcp__mentor__list_goals",
            "mcp__mentor__add_task",
            "mcp__mentor__complete_task",
        ],
    )


async def run_query(prompt: str, store: TaskStore, user_name: str = "the user") -> str:
    options = build_options(store, user_name=user_name)
    result_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result
    return result_text
