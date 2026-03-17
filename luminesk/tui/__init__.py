from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
	from .app import LumiNESKTuiApp, run_tui


__all__ = ["LumiNESKTuiApp", "run_tui"]


def __getattr__(name: str):
	if name == "LumiNESKTuiApp":
		from .app import LumiNESKTuiApp

		return LumiNESKTuiApp

	if name == "run_tui":
		from .app import run_tui

		return run_tui

	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
