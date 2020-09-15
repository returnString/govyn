from typing import Optional, List, Union, Dict, Any, Literal
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

import pytest
from starlette.testclient import TestClient

from .helpers import make_client

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

@dataclass
class OptionalTypes:
	maybe_str_field: Optional[str]

StringEnum = Literal["type1", "type2", "type3"]

@dataclass
class EnumTypes:
	string_enum_field: StringEnum

@dataclass
class StdLibTypes:
	datetime_field: datetime

class EchoAPI:
	async def get_scalars(self, str_field: str, int_field: int, float_field: float, bool_field: bool) -> ScalarTypes:
		return ScalarTypes(str_field, int_field, float_field, bool_field)

	async def post_scalars(self, body: ScalarTypes) -> ScalarTypes:
		return body

	async def post_collections(self, body: CollectionTypes) -> CollectionTypes:
		return body

	async def get_optional(self, maybe_str_field: Optional[str]) -> OptionalTypes:
		return OptionalTypes(maybe_str_field)

	async def post_optional(self, body: OptionalTypes) -> OptionalTypes:
		return body

	async def get_list(self, numbers: List[int]) -> List[int]:
		return numbers

	async def get_enums(self, string_selection: StringEnum) -> EnumTypes:
		return EnumTypes(string_selection)

	async def post_enums(self, body: EnumTypes) -> EnumTypes:
		return body

	async def get_stdlib_types(self, datetime_field: datetime) -> StdLibTypes:
		return StdLibTypes(datetime_field)

	async def post_stdlib_types(self, body: StdLibTypes) -> StdLibTypes:
		return body

client = make_client(EchoAPI)

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

def test_get_optional_present(client: TestClient) -> None:
	example_optional = asdict(OptionalTypes('string'))
	res = client.get('/optional', params = example_optional)
	assert res.status_code == 200
	assert res.json() == example_optional

def test_get_optional_missing(client: TestClient) -> None:
	example_optional = asdict(OptionalTypes(None))
	res = client.get('/optional', params = example_optional)
	assert res.status_code == 200
	assert res.json() == example_optional

def test_post_optional_present(client: TestClient) -> None:
	example_optional = asdict(OptionalTypes('string'))
	res = client.post('/optional', json = example_optional)
	assert res.status_code == 200
	assert res.json() == example_optional

def test_post_optional_missing(client: TestClient) -> None:
	example_optional = asdict(OptionalTypes(None))
	res = client.post('/optional', json = example_optional)
	assert res.status_code == 200
	assert res.json() == example_optional

def test_get_raw_list(client: TestClient) -> None:
	example_list = [ 1, 2, 3 ]
	res = client.get('/list', params = { 'numbers': example_list })
	assert res.status_code == 200
	assert res.json() == example_list

def test_get_enum(client: TestClient) -> None:
	example_enums = EnumTypes('type1')
	res = client.get('/enums', params = { 'string_selection': example_enums.string_enum_field })
	assert res.status_code == 200
	assert res.json() == asdict(example_enums)

def test_get_enum_invalid_option(client: TestClient) -> None:
	example_enums = EnumTypes('not an option') # type: ignore
	res = client.get('/enums', params = { 'string_selection': example_enums.string_enum_field })
	assert res.status_code == 400

def test_post_enum(client: TestClient) -> None:
	example_enums = asdict(EnumTypes('type1'))
	res = client.post('/enums', json = example_enums)
	assert res.status_code == 200
	assert res.json() == example_enums

def test_post_enum_invalid(client: TestClient) -> None:
	example_enums = asdict(EnumTypes('not an option')) # type: ignore
	res = client.post('/enums', json = example_enums)
	assert res.status_code == 400

def test_get_stdlib_types(client: TestClient) -> None:
	example = StdLibTypes(datetime.now())
	res = client.get('/stdlib_types', params = { 'datetime_field': example.datetime_field.isoformat() })
	assert res.status_code == 200
	res_data = res.json()
	res_data['datetime_field'] = datetime.fromisoformat(res_data['datetime_field'])
	assert res_data == asdict(example)

def test_post_stdlib_types(client: TestClient) -> None:
	example = asdict(StdLibTypes(datetime.now()))
	example['datetime_field'] = example['datetime_field'].isoformat()
	res = client.post('/stdlib_types', json = example)
	assert res.status_code == 200
	assert res.json() == example

def test_get_invalid_datetime(client: TestClient) -> None:
	res = client.get('/stdlib_types', params = { 'datetime_field': 'not a date' })
	assert res.status_code == 400

def test_post_invalid_datetime(client: TestClient) -> None:
	res = client.post('/stdlib_types', json = { 'datetime_field': 'not a date' })
	assert res.status_code == 400
