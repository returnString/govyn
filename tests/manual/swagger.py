from dataclasses import dataclass
from typing import Optional, Literal

from govyn import create_app, run_app
from govyn.auth import Principal, HeaderAuthBackend

MyEnum = Literal['test string', 'other supported value']

@dataclass
class GreetingResponse:
	text: str
	enum_values: MyEnum

class TestUIServer:
	async def get_greeting(self, principal: Principal) -> GreetingResponse:
		return GreetingResponse(f'hey there, {principal.id}', 'test string')

class SuperInsecureAuthBackend(HeaderAuthBackend):
	header = 'Username'

	async def principal_from_header(self, value: str) -> Optional[Principal]:
		return Principal(value, set())

run_app(create_app(TestUIServer(), auth_backend = SuperInsecureAuthBackend()))
