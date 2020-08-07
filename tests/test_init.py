from typing import Optional, List, Union, Dict, Any, Generator
from dataclasses import dataclass, asdict

import pytest
from starlette.testclient import TestClient

from govyn import create_app

@dataclass
class Response:
	boot_value: int

class AsyncInitAPI:
	async def startup(self) -> None:
		self.required_value = 1

	async def get(self) -> Response:
		return Response(self.required_value)

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
	with TestClient(create_app(AsyncInitAPI())) as c:
		yield c # type: ignore

def test_async_startup(client: TestClient) -> None:
	res = client.get('/')
	assert res.status_code == 200
	assert res.json() == asdict(Response(1))
