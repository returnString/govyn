from typing import Optional
from dataclasses import dataclass, asdict

import pytest
from starlette.testclient import TestClient

from govyn.auth import Principal, HeaderAuthBackend, privileged

from .helpers import make_client

class HardcodedAuthBackend(HeaderAuthBackend):
	header = "Govyn-Token"

	async def startup(self) -> None:
		self.tokens = {
			'1234': Principal('user1', set()),
			'5678': Principal('user2', { 'super_secret_access' }),
		}

	async def principal_from_header(self, token: str) -> Optional[Principal]:
		return self.tokens.get(token)

@dataclass
class AuthedResponse:
	name: str

@dataclass
class AuthAPI:
	async def get(self, principal: Principal) -> AuthedResponse:
		return AuthedResponse(principal.id)

	@privileged('super_secret_access')
	async def get_supersecret(self, principal: Principal) -> AuthedResponse:
		return AuthedResponse('hot take')

client = make_client(AuthAPI, auth_backend = HardcodedAuthBackend())

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

def test_privileges(client: TestClient) -> None:
	res = client.get('/supersecret', headers = { 'Govyn-Token': '5678' })
	assert res.status_code == 200
	assert res.json() == asdict(AuthedResponse('hot take'))

def test_privileges_insufficient(client: TestClient) -> None:
	res = client.get('/supersecret', headers = { 'Govyn-Token': '1234' })
	assert res.status_code == 403
