from dataclasses import dataclass

import pytest
from govyn.errors import BadRequest
from starlette.testclient import TestClient

from .helpers import make_client


@dataclass
class EmptyRequest():
	pass

@dataclass
class EmptyResponse():
	pass

class ErrorAPI:
	async def get_error(self) -> EmptyResponse:
		raise BadRequest('This is a bad request', data=dict(foo='bar'))

	async def post_error(self, x: EmptyRequest) -> EmptyResponse:
		raise BadRequest('This is a bad request', data=dict(foo='bar'))

	async def get_internal_error(self) -> float:
		return 10 / 0

client = make_client(ErrorAPI)

def test_get_http_error(client: TestClient) -> None:
	'''
	Test that an HTTPError is handled appropriately (is jsonified)
	for get requests
	'''
	res = client.get('/error')
	assert res.status_code == 400
	assert res.json() == {
		'error_type': 'Bad Request',
		'error_description': 'This is a bad request',
		'error_data': {'foo': 'bar'}
	}

def test_post_http_error(client: TestClient) -> None:
	'''
	Test that an HTTPError is handled appropriately (is jsonified)
	for post requests
	'''

	res = client.post('/error', json={})
	assert res.status_code == 400
	assert res.json() == {
		'error_type': 'Bad Request',
		'error_description': 'This is a bad request',
		'error_data': {'foo': 'bar'}
	}

def test_500_error(client: TestClient) -> None:
	res = client.get('/internal_error')
	assert res.status_code == 500
