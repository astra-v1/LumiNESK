from __future__ import annotations

import shutil
import subprocess

from luminesk.core.messages import t


def build_tmux_session_name(tag: str) -> str:
	sanitized = "".join(
		char if char.isalnum() or char in {"-", "_"} else "-"
		for char in tag.strip().lower()
	).strip("-_")
	return f"luminesk-{sanitized or 'server'}"


def build_tmux_attach_command(session_name: str) -> tuple[str, ...]:
	return ("tmux", "attach-session", "-t", session_name)


def send_tmux_command(session_name: str, command: str) -> None:
	tmux_bin = shutil.which("tmux")
	if tmux_bin is None:
		raise RuntimeError(t("tmux.not_found"))

	literal_result = subprocess.run(
		[tmux_bin, "send-keys", "-t", session_name, "-l", command],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.PIPE,
		text=True,
		encoding="utf-8",
		errors="replace",
		check=False,
	)
	if literal_result.returncode != 0:
		raise RuntimeError(literal_result.stderr.strip() or t("tmux.send_keys_failed"))

	enter_result = subprocess.run(
		[tmux_bin, "send-keys", "-t", session_name, "Enter"],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.PIPE,
		text=True,
		encoding="utf-8",
		errors="replace",
		check=False,
	)
	if enter_result.returncode != 0:
		raise RuntimeError(enter_result.stderr.strip() or t("tmux.send_enter_failed"))


def tmux_session_exists(session_name: str) -> bool:
	tmux_bin = shutil.which("tmux")
	if tmux_bin is None:
		return False

	result = subprocess.run(
		[tmux_bin, "has-session", "-t", session_name],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
		check=False,
	)
	return result.returncode == 0
