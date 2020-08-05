from typing import Optional, List, Union
from dataclasses import dataclass

import govyn
from govyn.errors import BadRequest

@dataclass
class TestInput:
	name: str

@dataclass
class TestResponse:
	name: str
	id: int
	values: List[int]
	is_set: bool = False

@dataclass
class UnionResponse:
	many_types: Union[str, int, float]

@dataclass
class EmptyResponse:
	pass

@dataclass
class ExampleAPI:
	async def get(self) -> TestResponse:
		'''Get the root response'''
		return TestResponse('root', 1, [])

	async def get_test(self, test_name: Optional[str], test_num: Optional[int]) -> TestResponse:
		'''Get a customised response'''
		return TestResponse(test_name or "unknown", test_num or 1, [ 1, 2, 3 ])

	async def post_test(self, test_input: TestInput) -> TestResponse:
		'''Submit an input'''
		return TestResponse(test_input.name, 1, [ 1, 2, 3 ])

	async def get_union(self) -> UnionResponse:
		'''Get a union'''
		return UnionResponse(1)

	async def get_binarychoice(self, is_set: bool) -> EmptyResponse:
		return EmptyResponse()

	async def get_exception(self) -> EmptyResponse:
		raise BadRequest('an explanation')

	async def get_exception_data(self) -> EmptyResponse:
		raise BadRequest('an explanation', { 'test': 1 })

govyn.run(ExampleAPI())
