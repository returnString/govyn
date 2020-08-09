from dataclasses import dataclass, asdict

import pytest
from starlette.testclient import TestClient

from .helpers import make_client

@dataclass
class Response:
	boot_value: int

class AsyncInitAPI:
	async def startup(self) -> None:
		self.required_value = 1

	async def get(self) -> Response:
		return Response(self.required_value)

client = make_client(AsyncInitAPI)

def test_async_startup(client: TestClient) -> None:
	res = client.get('/')
	assert res.status_code == 200
	assert res.json() == asdict(Response(1))
