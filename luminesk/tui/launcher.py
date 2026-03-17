from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from luminesk.core.messages import t
from luminesk.utils.tmux import (
	build_tmux_attach_command,
	build_tmux_session_name,
)


APP_ROOT = Path(__file__).resolve().parents[2]


class ServerLaunchTarget(Protocol):
	tag: str
	path: Path


@dataclass(slots=True, frozen=True)
class DetachedLaunchResult:
	session_name: str
	command: tuple[str, ...]
	attach_command: tuple[str, ...]
	log_path: Path


def build_start_command(tag: str, loop: bool = False) -> tuple[str, ...]:
	command = [sys.executable, "-m", "luminesk", "start", "--tag", tag]
	if loop:
		command.append("--loop")
	return tuple(command)


def build_launch_environment(app_root: Path = APP_ROOT) -> dict[str, str]:
	env = os.environ.copy()
	app_root_str = str(app_root)
	existing_pythonpath = env.get("PYTHONPATH", "")

	if not existing_pythonpath:
		env["PYTHONPATH"] = app_root_str
		return env

	parts = existing_pythonpath.split(os.pathsep)
	if app_root_str not in parts:
		env["PYTHONPATH"] = os.pathsep.join((app_root_str, existing_pythonpath))

	return env


def build_log_path(server: ServerLaunchTarget, now: datetime | None = None) -> Path:
	timestamp = (now or datetime.now().astimezone()).strftime("%Y%m%d-%H%M%S")
	return server.path / ".luminesk" / "logs" / f"{server.tag}-{timestamp}.log"


def build_tmux_command(
	server: ServerLaunchTarget,
	log_path: Path,
	loop: bool = False,
	app_root: Path = APP_ROOT,
) -> tuple[str, ...]:
	env = build_launch_environment(app_root)
	start_command = [
		"env",
		f"PYTHONPATH={env['PYTHONPATH']}",
		*build_start_command(server.tag, loop=loop),
	]
	session_command = " ".join(shlex.quote(part) for part in start_command)
	log_parent = shlex.quote(str(log_path.parent))
	log_target = shlex.quote(str(log_path))
	return (
		"bash",
		"-lc",
		f"mkdir -p {log_parent} && exec {session_command} 2>&1 | tee -a {log_target}",
	)


def launch_server_detached(
	server: ServerLaunchTarget,
	loop: bool = False,
	app_root: Path = APP_ROOT,
) -> DetachedLaunchResult:
	tmux_bin = shutil.which("tmux")
	if tmux_bin is None:
		raise RuntimeError(t("launcher.tmux_not_found"))

	log_path = build_log_path(server)
	log_path.parent.mkdir(parents=True, exist_ok=True)
	command = build_tmux_command(server, log_path, loop=loop, app_root=app_root)
	session_name = build_tmux_session_name(server.tag)
	attach_command = build_tmux_attach_command(session_name)

	with log_path.open("a", encoding="utf-8") as log_file:
		log_file.write(
			f"[{datetime.now().astimezone().isoformat()}] Launching tmux session {session_name}: "
			f"{' '.join(command)}\n"
		)
		subprocess.run(
			[
				tmux_bin,
				"new-session",
				"-d",
				"-s",
				session_name,
				"-c",
				str(server.path),
				*command,
			],
			check=True,
			stdout=log_file,
			stderr=subprocess.STDOUT,
			text=True,
		)

	return DetachedLaunchResult(
		session_name=session_name,
		command=command,
		attach_command=attach_command,
		log_path=log_path,
	)
