# Mentor Agent

A personal AI mentor, built on the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview).

It keeps a persistent record of your goals and tasks, and gives you a direct, prioritized
morning briefing instead of a generic to-do list — built for someone running a career
and a business at the same time, who needs a mentor that pushes back, not a planner that
just nods along.

## Features

- **Persistent memory** — goals and tasks are stored locally (`~/.mentor_agent/data.json`)
  and read by the agent before every response, so it never gives advice blind.
- **Morning briefing** — `mentor brief` asks Claude to pull your goals/tasks and hand back
  a single prioritized plan: what to do first, why, and what's at risk of slipping.
- **Mentor chat** — `mentor chat "..."` for ad-hoc advice, with the same tool access.
- **Agentic, not scripted** — Claude decides when to read or update your task list via
  real tool calls (`list_tasks`, `list_goals`, `add_task`, `complete_task`), not a fixed
  template.

## Setup

```bash
# 1. Install
pip install -e .

# 2. Configure your API key
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY (from https://platform.claude.com/)
export $(cat .env | xargs)

# 3. (If the SDK can't find a CLI binary on your machine) install the Claude Code CLI,
#    which the Python Agent SDK shells out to:
npm install -g @anthropic-ai/claude-code
```

Requires Python 3.10+.

## Usage

```bash
# Tell it what you're working toward
mentor add-goal "Land a senior role in London" --category career
mentor add-goal "Get the business to first revenue" --category business

# Add tasks as they come up
mentor add-task "Send follow-up to recruiter" --category career --priority 1 --due 2026-07-01
mentor add-task "Finish pitch deck" --category business --priority 1

# Every morning
mentor brief

# Anytime
mentor chat "I'm stuck between two job offers, how do I think about this?"

# Manage tasks directly
mentor tasks
mentor done <task-id>
```

Pass `--name "Ugluu"` to any command to have the mentor address you by name.

## Automating the morning briefing

`mentor brief` is just a CLI command, so you can schedule it with cron (Linux/macOS) or
Task Scheduler (Windows). For example, to run it at 7:00 AM daily and save the output:

```cron
0 7 * * * cd /path/to/mentor-agent && /usr/bin/env mentor brief --name "Ugluu" >> ~/mentor-agent/briefings.log 2>&1
```

Piping that into a notification (email, Slack webhook, push notification) is a natural
next step — see Roadmap.

## Architecture

```
src/mentor_agent/
  memory.py   # TaskStore: JSON-backed goals/tasks/briefing history
  agent.py    # System prompt + Claude Agent SDK tools + query() entrypoint
  cli.py      # argparse CLI (brief, chat, add-goal, add-task, tasks, done)
```

The agent has no special access beyond four narrow tools scoped to your own task store —
it cannot read your filesystem, run shell commands, or browse the web. That's deliberate:
a mentor that manages your priorities doesn't need broader system access.

## Roadmap

- [ ] Multi-turn `chat` that resumes the same session instead of starting fresh each call
- [ ] Calendar integration (Google Calendar) so the briefing accounts for actual meetings
- [ ] Weekly retro: review completed vs. dropped tasks and goal progress
- [ ] Push notifications (e.g. ntfy.sh) instead of cron + log file
- [ ] Optional voice input/output for the chat command

## License

MIT — see [LICENSE](LICENSE).
