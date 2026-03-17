from datetime import timedelta
from pathlib import Path

import pytest

from luminesk.core.manager import (
	ServerManagerError,
	_detect_core_id,
	_extract_file_name_from_content_disposition,
	_parse_content_length,
	_read_cached_file_name,
	_resolve_server_jar_path,
	_sanitize_cache_component,
	format_timedelta,
)


def test_format_timedelta() -> None:
	assert format_timedelta(None) == "—"
	assert format_timedelta(timedelta(hours=1, minutes=2, seconds=3)) == "01:02:03"


def test_sanitize_cache_component() -> None:
	assert _sanitize_cache_component("  ..v1.0/rc1.. ") == "v1.0-rc1"
	assert _sanitize_cache_component("   ") == "latest"


def test_read_cached_file_name(tmp_path: Path) -> None:
	metadata_path = tmp_path / "meta.json"
	metadata_path.write_text('{"file_name": "core.jar"}', encoding="utf-8")
	assert _read_cached_file_name(metadata_path) == "core.jar"

	metadata_path.write_text('{"file_name": "dir/core.jar"}', encoding="utf-8")
	assert _read_cached_file_name(metadata_path) is None

	metadata_path.write_text('{"file_name": "core.zip"}', encoding="utf-8")
	assert _read_cached_file_name(metadata_path) is None


def test_extract_file_name_from_content_disposition() -> None:
	assert (
		_extract_file_name_from_content_disposition("attachment; filename=\"core.jar\"")
		== "core.jar"
	)
	assert (
		_extract_file_name_from_content_disposition("attachment; filename*=UTF-8''Lumi%20Core.jar")
		== "Lumi Core.jar"
	)


def test_parse_content_length() -> None:
	assert _parse_content_length(None) is None
	assert _parse_content_length("123") == 123
	assert _parse_content_length("nope") is None


def test_resolve_server_jar_path(tmp_path: Path) -> None:
	jar = tmp_path / "server.jar"
	jar.write_text("data", encoding="utf-8")
	resolved = _resolve_server_jar_path(tmp_path, Path("server.jar"))
	assert resolved == jar.resolve()

	outside = tmp_path.parent / "outside.jar"
	outside.write_text("data", encoding="utf-8")
	with pytest.raises(ServerManagerError):
		_resolve_server_jar_path(tmp_path, outside)


def test_detect_core_id_prefers_config_file(tmp_path: Path) -> None:
	(tmp_path / "pnx.yml").write_text("config", encoding="utf-8")
	jar = tmp_path / "server.jar"
	jar.write_text("data", encoding="utf-8")
	assert _detect_core_id(tmp_path, jar) == "pnx"


def test_detect_core_id_uses_jar_name(tmp_path: Path) -> None:
	jar = tmp_path / "PowerNukkitX-1.0.jar"
	jar.write_text("data", encoding="utf-8")
	assert _detect_core_id(tmp_path, jar) == "pnx"
