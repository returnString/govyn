from dataclasses import dataclass
from typing import Optional, Literal

from govyn import run
from govyn.auth import Principal, HeaderAuthBackend
from govyn.metrics import Counter

MyEnum = Literal['test string', 'other supported value']

@dataclass
class GreetingResponse:
	text: str
	enum_values: MyEnum

class TestUIServer:
	async def startup(self) -> None:
		self.greeting_counter = Counter('num_greetings')

	async def get_greeting(self, principal: Principal) -> GreetingResponse:
		'''Longer description of getting a greeting.'''

		self.greeting_counter.inc(
			name = principal.id,
		)

		return GreetingResponse(f'hey there, {principal.id}', 'test string')

class SuperInsecureAuthBackend(HeaderAuthBackend):
	header = 'Username'

	async def principal_from_header(self, value: str) -> Optional[Principal]:
		return Principal(value, set())

run(TestUIServer(), auth_backend = SuperInsecureAuthBackend())
