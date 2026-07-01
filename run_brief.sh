#!/bin/zsh
cd ~/Projects/AI\ Agent/mentor-agent
source .venv/bin/activate
set -a
source .env
set +a
export FORCE_COLOR=1
mentor --name "Ugluu" brief >> ~/mentor-brief.log 2>&1
