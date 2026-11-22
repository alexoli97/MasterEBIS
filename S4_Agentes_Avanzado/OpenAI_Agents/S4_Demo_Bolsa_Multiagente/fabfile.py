"""Fabric SSH deploy tasks.

Usage:
    fab -H user@host deploy
    fab -H user@host restart
    fab -H user@host down
    fab -H user@host logs
    fab -H user@host status

Requires DEPLOY_HOST + DEPLOY_PATH in .env (or pass via -H / cli).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from fabric import Connection, task
from invoke import Context

load_dotenv()

DEFAULT_PATH = os.getenv("DEPLOY_PATH", "/opt/bolsa")


@task
def build(c: Context) -> None:
    """Local docker build."""
    c.run("docker compose build")


@task
def push(c: Connection) -> None:
    """Rsync project to remote host (excludes .venv, .git, .env)."""
    path = DEFAULT_PATH
    c.local(
        f"rsync -avz --delete "
        f"--exclude '.venv' --exclude '__pycache__' --exclude '.git' "
        f"--exclude '.env' --exclude 'data/cache' "
        f"./ {c.user}@{c.host}:{path}/"
    )
    # .env handled separately if not present
    c.run(f"test -f {path}/.env || cp {path}/.env.example {path}/.env")


@task
def deploy(c: Connection) -> None:
    """Push code, rebuild image, restart container."""
    push(c)
    with c.cd(DEFAULT_PATH):
        c.run("docker compose build")
        c.run("docker compose up -d")


@task
def restart(c: Connection) -> None:
    with c.cd(DEFAULT_PATH):
        c.run("docker compose restart")


@task
def stop(c: Connection) -> None:
    with c.cd(DEFAULT_PATH):
        c.run("docker compose down")


@task
def down(c: Context) -> None:
    """Stop and remove containers, networks (docker compose down).

    Local (`fab down`) runs in cwd. Remote (`fab -H ... down`) cd to DEPLOY_PATH.
    """
    if isinstance(c, Connection):
        with c.cd(DEFAULT_PATH):
            c.run("docker compose down")
    else:
        c.run("docker compose down")


@task
def logs(c: Connection, tail: str = "200") -> None:
    with c.cd(DEFAULT_PATH):
        c.run(f"docker compose logs --tail={tail} -f bolsa", pty=True)


@task
def status(c: Connection) -> None:
    with c.cd(DEFAULT_PATH):
        c.run("docker compose ps")
