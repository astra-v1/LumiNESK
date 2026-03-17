from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def create_app() -> FastAPI:
	app = FastAPI(title="LumiNESK GUI")
	app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
	app.include_router(router)
	return app


def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
	import uvicorn

	uvicorn.run(
		"luminesk.gui.app:create_app",
		factory=True,
		host=host,
		port=port,
		reload=reload,
	)
