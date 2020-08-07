from typing import Optional, List, Union, Dict
from dataclasses import dataclass, asdict

import pytest
from starlette.testclient import TestClient

from govyn import create_app
from govyn.auth import Principal, HeaderAuthBackend

class HardcodedAuthBackend(HeaderAuthBackend):
	def __init__(self) -> None:
		super().__init__("Govyn-Token")
		self.tokens = {
			'1234': 'user1',
			'5678': 'user2',
		}

	async def principal_from_header(self, token: str) -> Optional[Principal]:
		principal_id = self.tokens.get(token)
		if principal_id is None:
			return None

		return Principal(principal_id)

@dataclass
class AuthedResponse:
	name: str

@dataclass
class AuthAPI:
	async def get(self, principal: Principal) -> AuthedResponse:
		return AuthedResponse(principal.id)

@pytest.fixture
def client() -> TestClient:
	return TestClient(create_app(AuthAPI(), auth_backend = HardcodedAuthBackend()))

def test_token(client: TestClient) -> None:
	res = client.get('/', headers = { 'Govyn-Token': '1234' })
	assert res.status_code == 200
	assert res.json() == asdict(AuthedResponse('user1'))
	
	res = client.get('/', headers = { 'Govyn-Token': '5678' })
	assert res.status_code == 200
	assert res.json() == asdict(AuthedResponse('user2'))

def test_token_invalid(client: TestClient) -> None:
	res = client.get('/', headers = { 'Govyn-Token': 'not a token' })
	assert res.status_code == 401

def test_token_missing(client: TestClient) -> None:
	res = client.get('/')
	assert res.status_code == 401
