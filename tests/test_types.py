from typing import Optional, List, Union, Dict, Any
from dataclasses import dataclass, asdict

import pytest
from starlette.testclient import TestClient

from govyn import create_app

@dataclass
class ScalarTypes:
	str_field: str
	int_field: int
	float_field: float
	bool_field: bool

@dataclass
class CollectionTypes:
	dict_field: Dict[str, int]
	list_field: List[bool]
	union_field: Union[str, int]

class EchoAPI:
	async def get_scalars(self, str_field: str, int_field: int, float_field: float, bool_field: bool) -> ScalarTypes:
		return ScalarTypes(str_field, int_field, float_field, bool_field)

	async def post_scalars(self, body: ScalarTypes) -> ScalarTypes:
		return body

	async def post_collections(self, body: CollectionTypes) -> CollectionTypes:
		return body

@pytest.fixture
def client() -> TestClient:
	return TestClient(create_app(EchoAPI()))

@pytest.fixture
def example_scalars() -> Dict[str, Any]:
	return asdict(ScalarTypes('test_str', 123, 1.5, False))

@pytest.fixture
def example_collections() -> Dict[str, Any]:
	return asdict(CollectionTypes({ 'key1': 123, 'key2': 456 }, [ True, False, True ], 'str variant'))

def test_get(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	res = client.get('/scalars', params = example_scalars)
	assert res.status_code == 200
	assert res.json() == example_scalars

def test_get_missing_field(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	del example_scalars['str_field']
	res = client.get('/scalars', params = example_scalars)
	assert res.status_code == 400

def test_get_invalid_types(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	example_scalars['bool_field'] = 'not a bool'
	res = client.get('/scalars', params = example_scalars)
	assert res.status_code == 400

def test_post(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	res = client.post('/scalars', json = example_scalars)
	assert res.status_code == 200
	assert res.json() == example_scalars

def test_post_missing_field(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	del example_scalars['int_field']
	res = client.post('/scalars', json = example_scalars)
	assert res.status_code == 400

def test_post_invalid_types(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	example_scalars['str_field'] = 100
	res = client.post('/scalars', json = example_scalars)
	assert res.status_code == 400

def test_post_collections(client: TestClient, example_collections: Dict[str, Any]) -> None:
	res = client.post('/collections', json = example_collections)
	assert res.status_code == 200
	assert res.json() == example_collections

def test_post_invalid_union(client: TestClient, example_collections: Dict[str, Any]) -> None:
	example_collections['union_field'] = 1.5
	res = client.post('/collections', json = example_collections)
	assert res.status_code == 400

def test_post_invalid_dict(client: TestClient, example_collections: Dict[str, Any]) -> None:
	example_collections['dict_field'] = []
	res = client.post('/collections', json = example_collections)
	assert res.status_code == 400

def test_post_invalid_list(client: TestClient, example_collections: Dict[str, Any]) -> None:
	example_collections['list_field'] = {}
	res = client.post('/collections', json = example_collections)
	assert res.status_code == 400
