from dataclasses import dataclass

import govyn

@dataclass
class Response:
	boot_value: int

class AsyncInitExampleAPI:
	async def init(self) -> None:
		self.required_value = 1

	async def get(self) -> Response:
		return Response(self.required_value)

govyn.run(AsyncInitExampleAPI())
