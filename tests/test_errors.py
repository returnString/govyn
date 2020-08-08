from typing import Generator
from dataclasses import dataclass

import pytest
from starlette.testclient import TestClient

from govyn import create_app

@dataclass
class Response:
	pass

class ErrorAPI:
	async def get_500(self) -> Response:
		raise Exception('boom')

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
	with TestClient(create_app(ErrorAPI())) as c:
		yield c # type: ignore

def test_500(client: TestClient) -> None:
	res = client.get('/500')
	assert res.status_code == 500
	print(res.text)
