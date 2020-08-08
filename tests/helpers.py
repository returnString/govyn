from typing import Any, Generator, Optional, Callable

import pytest
from starlette.testclient import TestClient

from govyn import create_app
from govyn.auth import AuthBackend

def make_client(srv: Callable[[], Any], auth_backend: Optional[AuthBackend] = None) -> Any:
	@pytest.fixture
	def _client() -> Any:
		with TestClient(create_app(srv(), auth_backend = auth_backend)) as c:
			yield c
	return _client
