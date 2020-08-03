from typing import Optional, List
from dataclasses import dataclass

import govyn

@dataclass
class TestInput:
	name: str

@dataclass
class TestResponse:
	name: str
	id: int
	values: List[int]

@dataclass
class ExampleAPI:
	async def get(self) -> TestResponse:
		return TestResponse('root', 1, [])

	async def get_test(self, test_name: Optional[str], test_num: Optional[int]) -> TestResponse:
		return TestResponse(test_name or "unknown", test_num or 1, [ 1, 2, 3 ])

	async def post_test(self, test_input: TestInput) -> TestResponse:
		return TestResponse(test_input.name, 1, [ 1, 2, 3 ])

govyn.run(ExampleAPI())
