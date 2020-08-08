from typing import Set, Optional, Dict, Protocol, Callable, TypeVar, Any, cast
from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import wraps

from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .errors import Unauthorised, Forbidden

@dataclass
class Principal:
	id: str
	privileges: Set[str]

class AuthBackend(Protocol):
	async def resolve_principal(self, req: Request) -> Optional[Principal]:
		...

class AuthMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: ASGIApp, auth_backend: AuthBackend) -> None:
		super().__init__(app)
		self.auth_backend = auth_backend

	async def dispatch(self, req: Request, call_next: RequestResponseEndpoint) -> Response:
		principal = await self.auth_backend.resolve_principal(req)
		if principal is None:
			raise Unauthorised('authentication failed')

		req.state.principal = principal
		return await call_next(req)

class HeaderAuthBackend(ABC):
	def __init__(self, header: str) -> None:
		self.header = header

	async def resolve_principal(self, req: Request) -> Optional[Principal]:
		token = req.headers.get(self.header)
		if not token:
			raise Unauthorised(f'missing header: {self.header}')

		return await self.principal_from_header(token)

	@abstractmethod
	async def principal_from_header(self, value: str) -> Optional[Principal]:
		...

TFunc = TypeVar('TFunc', bound = Callable[..., Any])

def privileged(privilege: str) -> Callable[[ TFunc ], TFunc]:
	def _decorator(func: TFunc) -> TFunc:
		@wraps(func)
		async def _impl(*args: Any, **kwargs: Any) -> Any:
			principal = cast(Principal, kwargs['principal'])
			if privilege not in principal.privileges:
				raise Forbidden('insufficient privileges')

			return await func(*args, **kwargs)

		return cast(TFunc, _impl)
	return _decorator
