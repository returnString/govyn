from typing import Any, Callable, Generator, Optional

import pytest
from govyn.app import create_app
from govyn.auth import AuthBackend
from starlette.testclient import TestClient


def make_client(srv: Callable[[], Any], auth_backend: Optional[AuthBackend] = None) -> Any:
	@pytest.fixture
	def _client() -> Any:
		with TestClient(create_app(srv(), auth_backend = auth_backend), raise_server_exceptions=False) as c:
			yield c
	return _client
