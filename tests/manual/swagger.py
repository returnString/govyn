from dataclasses import dataclass
from typing import Optional, Literal, Dict

from govyn import run
from govyn.auth import Principal, HeaderAuthBackend
from govyn.metrics import MetricsRegistry

MyEnum = Literal['test string', 'other supported value']

@dataclass
class GreetingResponse:
	text: str
	enum_values: MyEnum

class TestUIServer:
	def __init__(self) -> None:
		self.metrics = MetricsRegistry()

	async def startup(self) -> None:
		self.greeting_counter = self.metrics.counter('num_greetings')

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

	def principal_metric_labels(self, principal: Principal) -> Dict[str, str]:
		return {
			'test_extra_label': principal.id,
		}

run(TestUIServer(), auth_backend = SuperInsecureAuthBackend())
