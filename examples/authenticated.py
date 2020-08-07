from typing import Optional, List, Union, Dict
from dataclasses import dataclass

import govyn
from govyn.errors import Unauthorised
from govyn.auth import Principal, HeaderAuthBackend

class TestAuthBackend(HeaderAuthBackend):
	def __init__(self, header: str, tokens: Dict[str, str]) -> None:
		super().__init__(header)
		self.tokens = tokens

	async def principal_from_header(self, token: str) -> Optional[Principal]:
		principal_id = self.tokens.get(token)
		if principal_id is None:
			raise Unauthorised('invalid token')
		return Principal(principal_id)

@dataclass
class AuthedResponse:
	name: str

@dataclass
class ExampleAPI:
	async def get(self, principal: Principal) -> AuthedResponse:
		return AuthedResponse(principal.id)

govyn.run(
	ExampleAPI(),
	auth_backend = TestAuthBackend('x-govyn-test', {
		'1234': 'user1',
		'5678': 'user2',
	}),
)
