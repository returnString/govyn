from typing import Set, Optional, Dict, Callable, TypeVar, Any, ClassVar, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .errors import Unauthorised
from .metrics import MetricsRegistry

_REQUIRES_PRIVILEGE_ATTR = '_requires_privilege'

@dataclass
class Principal:
	id: str
	privileges: Set[str]

class AuthBackend(ABC):
	@abstractmethod
	async def resolve_principal(self, req: Request) -> Optional[Principal]:
		...

	@abstractmethod
	def openapi_spec(self) -> Tuple[str, Dict[str, Any]]:
		...

	def principal_metric_labels(self, principal: Principal) -> Dict[str, str]:
		return {
			'principal': principal.id,
		}

class AuthMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: ASGIApp, auth_backend: AuthBackend, metrics_registry: MetricsRegistry) -> None:
		super().__init__(app)
		self.auth_backend = auth_backend
		self.principal_resolution_histogram = metrics_registry.histogram('api_auth_principal_resolution_seconds')

	async def dispatch(self, req: Request, call_next: RequestResponseEndpoint) -> Response:
		with self.principal_resolution_histogram.observe_time():
			principal = await self.auth_backend.resolve_principal(req)

		if principal is None:
			raise Unauthorised('authentication failed')

		req.state.principal = principal
		req.state.principal_labels = self.auth_backend.principal_metric_labels(principal)

		return await call_next(req)

class HeaderAuthBackend(AuthBackend):
	header: ClassVar[str]

	async def resolve_principal(self, req: Request) -> Optional[Principal]:
		token = req.headers.get(self.header)
		if not token:
			return None

		return await self.principal_from_header(token)

	def openapi_spec(self) -> Tuple[str, Dict[str, Any]]:
		return 'API key', {
			'type': 'apiKey',
			'in': 'header',
			'name': self.header,
		}

	@abstractmethod
	async def principal_from_header(self, value: str) -> Optional[Principal]:
		...

TFunc = TypeVar('TFunc', bound = Callable[..., Any])

def privileged(privilege: str) -> Callable[[ TFunc ], TFunc]:
	def _decorator(func: TFunc) -> TFunc:
		setattr(func, _REQUIRES_PRIVILEGE_ATTR, privilege)
		return func
	return _decorator
