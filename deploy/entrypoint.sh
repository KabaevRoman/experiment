#!/bin/sh
alembic upgrade head
# obviously not acceptable in prod deployment =)
fastapi run
