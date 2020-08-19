from typing import Optional, Any, Dict, Union, Awaitable, Callable
from dataclasses import dataclass

from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import aioprometheus

LabelValue = Union[str, int]

_svc: aioprometheus.Service

def _metrics_sync_init(svc: aioprometheus.Service) -> None:
	global _svc
	_svc = svc

def _register(obj: Any) -> None:
	global _svc
	_svc.register(obj)

@dataclass
class Counter:
	name: str
	description: str = ''

	def __post_init__(self) -> None:
		self.counter = aioprometheus.Counter(self.name, self.description)
		_register(self.counter)

	def inc(self, **labels: LabelValue) -> None:
		self.counter.inc(labels)

class MetricsMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: ASGIApp) -> None:
		super().__init__(app)
		self.request_counter = Counter('govyn_requests_total')

	async def dispatch(self, req: Request, call_next: RequestResponseEndpoint) -> Response:
		res = await call_next(req)
		self.request_counter.inc(
			path = req.url.path,
			status = res.status_code,
		)
		return res
