from __future__ import annotations

import time

from contextlib import contextmanager
from typing import Any, Iterator

import httpx


DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 3.0


def request_with_retries(
	client: httpx.Client,
	method: str,
	url: str,
	*,
	attempts: int = DEFAULT_RETRY_ATTEMPTS,
	delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
	raise_for_status: bool = False,
	retry_on_status: bool = False,
	**kwargs: Any,
) -> httpx.Response:
	last_exception: Exception | None = None

	for attempt in range(1, attempts + 1):
		try:
			response = client.request(method, url, **kwargs)
			if raise_for_status:
				try:
					response.raise_for_status()
				except httpx.HTTPStatusError as exc:
					last_exception = exc
					response.close()
					if retry_on_status and attempt < attempts:
						time.sleep(delay_seconds)
						continue
					raise
			elif retry_on_status and not response.is_success:
				response.close()
				if attempt < attempts:
					time.sleep(delay_seconds)
					continue
			return response
		except httpx.RequestError as exc:
			last_exception = exc
			if attempt < attempts:
				time.sleep(delay_seconds)
				continue
			raise

	if last_exception:
		raise last_exception

	raise RuntimeError("Request failed without an exception.")


@contextmanager
def stream_with_retries(
	client: httpx.Client,
	method: str,
	url: str,
	*,
	attempts: int = DEFAULT_RETRY_ATTEMPTS,
	delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
	**kwargs: Any,
) -> Iterator[httpx.Response]:
	last_exception: Exception | None = None

	for attempt in range(1, attempts + 1):
		try:
			with client.stream(method, url, **kwargs) as response:
				try:
					response.raise_for_status()
				except httpx.HTTPStatusError as exc:
					last_exception = exc
					if attempt < attempts:
						time.sleep(delay_seconds)
						continue
					raise
				yield response
				return
		except httpx.RequestError as exc:
			last_exception = exc
			if attempt < attempts:
				time.sleep(delay_seconds)
				continue
			raise

	if last_exception:
		raise last_exception

	raise RuntimeError("Stream request failed without an exception.")
