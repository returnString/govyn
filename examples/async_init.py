from dataclasses import dataclass

import govyn

@dataclass
class Response:
	boot_value: int

class AsyncInitExampleAPI:
	async def startup(self) -> None:
		self.required_value = 1

	async def shutdown(self) -> None:
		print('shutting down')

	async def get(self) -> Response:
		return Response(self.required_value)

govyn.run(AsyncInitExampleAPI())
