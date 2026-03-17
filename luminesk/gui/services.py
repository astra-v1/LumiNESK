from __future__ import annotations

from fastapi import HTTPException

from luminesk.core.config import ManagedServer, UserConfig
from luminesk.core.messages import set_language


def load_config() -> UserConfig:
	config = UserConfig.load()
	set_language(config.language)
	return config


def get_server_or_404(config: UserConfig, tag: str) -> ManagedServer:
	server = config.get_server_by_tag(tag)
	if server is None:
		raise HTTPException(status_code=404, detail=f"Server '{tag}' was not found.")
	return server

