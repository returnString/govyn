import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

import pytest
from dacite.core import from_dict
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
	maybe_int_field: Optional[int]
	maybe_float_field: Optional[float]
	maybe_bool_field: Optional[bool]
	maybe_datetime_field: Optional[datetime]
	maybe_date_field: Optional[date]

StringEnum = Literal["type1", "type2", "type3"]
class ActualEnum(Enum):
	a="A"
	b="B"

@dataclass
class EnumTypes:
	string_enum_field: StringEnum

@dataclass
class ActualEnumTypes:
	actual_enum_field: ActualEnum
	some_other_value: str = 'hello'

@dataclass
class StdLibTypes:
	datetime_field: datetime
	date_field: date


@dataclass
class UnionEntryStrField:
	field1: str

@dataclass
class UnionEntryIntField:
	field2: int

@dataclass
class UnionOfDataClasses:
	union_param: Union[UnionEntryStrField, UnionEntryIntField]

class EchoAPI:
	async def get_scalars(self, str_field: str, int_field: int, float_field: float, bool_field: bool) -> ScalarTypes:
		return ScalarTypes(str_field, int_field, float_field, bool_field)

	async def post_scalars(self, body: ScalarTypes) -> ScalarTypes:
		return body

	async def post_collections(self, body: CollectionTypes) -> CollectionTypes:
		return body

	async def get_optional(
		self,
		maybe_str_field: Optional[str],
		maybe_int_field: Optional[int],
		maybe_float_field: Optional[float],
		maybe_bool_field: Optional[bool],
		maybe_datetime_field: Optional[datetime],
		maybe_date_field: Optional[date]
	) -> OptionalTypes:
		return OptionalTypes(
			maybe_str_field, maybe_int_field, maybe_float_field, maybe_bool_field,
			maybe_datetime_field, maybe_date_field
		)

	async def post_optional(self, body: OptionalTypes) -> OptionalTypes:
		return body

	async def get_list(self, numbers: List[int]) -> List[int]:
		return numbers

	async def get_enums(self, string_selection: StringEnum) -> EnumTypes:
		return EnumTypes(string_selection)

	async def post_enums(self, body: EnumTypes) -> EnumTypes:
		return body

	async def get_actual_enums(self, e: ActualEnum) -> ActualEnum:
		return e

	async def post_actual_enums(self, body: ActualEnumTypes) -> ActualEnumTypes:
		return body

	async def get_stdlib_types(self, datetime_field: datetime, date_field: date) -> StdLibTypes:
		return StdLibTypes(datetime_field, date_field)

	async def post_stdlib_types(self, body: StdLibTypes) -> StdLibTypes:
		return body

	async def post_union_dataclass_param(self, body: UnionOfDataClasses) -> UnionOfDataClasses:
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

def test_post_invalid_json(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	data = json.dumps(example_scalars)
	# make the json invalid by removing the first brace
	messed_up_data = data.replace('{', '', 1)
	res = client.post(
		"/scalars",
		headers={'content-type': 'application/json'},
		data=messed_up_data
	)
	assert res.status_code == 400

def test_post_invalid_null_scalars(client: TestClient, example_scalars: Dict[str, Any]) -> None:
	for key in example_scalars:
		example_scalars[key] = None
	data = json.dumps(example_scalars)
	res = client.post(
		'/scalars', headers={'content_type': 'application/json'}, data=data
	)
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
	example_optional = asdict(OptionalTypes('string', 1, 0.1, True, datetime.now(), date.today()))
	example_optional['maybe_datetime_field'] = example_optional['maybe_datetime_field'].isoformat()
	example_optional['maybe_date_field'] = example_optional['maybe_date_field'].isoformat()
	res = client.get('/optional', params = example_optional)
	assert res.status_code == 200
	assert res.json() == example_optional

def test_get_optional_missing(client: TestClient) -> None:
	example_optional = asdict(OptionalTypes(None, None, None, None, None, None))
	res = client.get('/optional', params = example_optional)
	assert res.status_code == 200
	assert res.json() == example_optional

def test_post_optional_present(client: TestClient) -> None:
	example_optional = asdict(OptionalTypes('string', 1, 0.1, True, datetime.now(), date.today()))
	example_optional['maybe_datetime_field'] = example_optional['maybe_datetime_field'].isoformat()
	example_optional['maybe_date_field'] = example_optional['maybe_date_field'].isoformat()
	res = client.post('/optional', json = example_optional)
	print(res.json())
	assert res.status_code == 200
	assert res.json() == example_optional

def test_post_optional_missing(client: TestClient) -> None:
	example_optional = asdict(OptionalTypes(None, None, None, None, None, None))
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

def test_get_actual_enum(client: TestClient) -> None:
	example_enum_value = 'A'
	res = client.get('/actual_enums', params = {'e': example_enum_value})
	assert res.status_code == 200
	assert res.json() == example_enum_value

def test_get_actual_enum_invalid_option(client: TestClient) -> None:
	invalid_options = ('a', 'C')
	for opt in invalid_options:
		res = client.get('/actual_enums', params = {'e': opt})
		assert res.status_code == 400
		assert res.json()['error_description'].endswith("Must be one of ['A', 'B']")

def test_post_actual_enum(client: TestClient) -> None:
	example_enum_request = {
		'actual_enum_field': 'A'
	}
	res = client.post('/actual_enums', json = example_enum_request)
	assert res.status_code == 200
	assert res.json() == {
		'actual_enum_field': 'A',
		'some_other_value': 'hello'
	}

def test_post_actual_enum_invalid_option(client: TestClient) -> None:
	invalid_options = ('a', 'C')
	for opt in invalid_options:
		example_enum_request = {
			'actual_enum_field': opt
		}
		res = client.post('/actual_enums', json = example_enum_request)
		assert res.status_code == 400
		assert res.json()['error_description'] == f"'{opt}' is not a valid ActualEnum"

def test_get_stdlib_types(client: TestClient) -> None:
	example = StdLibTypes(datetime.now(), date.today())
	res = client.get('/stdlib_types', params = { 'datetime_field': example.datetime_field.isoformat(), 'date_field': example.date_field.isoformat() })
	assert res.status_code == 200
	res_data = res.json()
	res_data['datetime_field'] = datetime.fromisoformat(res_data['datetime_field'])
	res_data['date_field'] = date.fromisoformat(res_data['date_field'])
	assert res_data == asdict(example)

def test_post_stdlib_types(client: TestClient) -> None:
	example = asdict(StdLibTypes(datetime.now(), date.today()))
	example['datetime_field'] = example['datetime_field'].isoformat()
	example['date_field'] = example['date_field'].isoformat()
	res = client.post('/stdlib_types', json = example)
	assert res.status_code == 200
	assert res.json() == example

def test_get_invalid_datetime(client: TestClient) -> None:
	res = client.get('/stdlib_types', params = { 'datetime_field': 'not a date' })
	assert res.status_code == 400

def test_post_invalid_datetime(client: TestClient) -> None:
	res = client.post('/stdlib_types', json = { 'datetime_field': 'not a date' })
	assert res.status_code == 400

def test_post_invalid_null_stdlib_types(client: TestClient) -> None:
	example_original = asdict(StdLibTypes(datetime.now(), date.today()))
	for key in example_original:
		example_original[key] = example_original[key].isoformat()
	for invalid in (1, 0.1, False, None):
		for key in example_original:
			example = deepcopy(example_original)
			example[key] = invalid
			res = client.post('/stdlib_types', json = example)
			assert res.status_code == 400

def test_post_dataclass_union(client: TestClient) -> None:
	example_str = UnionOfDataClasses(UnionEntryStrField('test'))
	res = client.post('/union_dataclass_param', json = asdict(example_str))
	assert res.status_code == 200
	res_data = from_dict(UnionOfDataClasses, res.json())
	assert res_data == example_str

	example_int = UnionOfDataClasses(UnionEntryIntField(1))
	res = client.post('/union_dataclass_param', json = asdict(example_int))
	assert res.status_code == 200
	res_data = from_dict(UnionOfDataClasses, res.json())
	assert res_data == example_int
