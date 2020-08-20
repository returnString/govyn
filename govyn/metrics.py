from typing import Optional, Any, Dict, Union, Awaitable, Callable, Sequence
from dataclasses import dataclass
from time import perf_counter

from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import aioprometheus

Observation = Union[float, int] 
LabelValue = Union[str, int]

_svc: aioprometheus.Service
_const_labels: Dict[str, LabelValue]

def _metrics_sync_init(svc: aioprometheus.Service, **labels: LabelValue) -> None:
	global _svc, _const_labels
	_svc = svc
	_const_labels = labels

@dataclass
class Counter:
	name: str
	description: str = ''

	def __post_init__(self) -> None:
		self.counter = aioprometheus.Counter(self.name, self.description, _const_labels)
		_svc.register(self.counter)

	def inc(self, **labels: LabelValue) -> None:
		self.counter.inc(labels)

@dataclass
class Histogram:
	name: str
	description: str = ''
	buckets: Sequence[float] = aioprometheus.Histogram.DEFAULT_BUCKETS

	def __post_init__(self) -> None:
		self.summary = aioprometheus.Histogram(self.name, self.description, _const_labels, buckets = self.buckets)
		_svc.register(self.summary)

	def observe(self, obs: Observation, **labels: LabelValue) -> None:
		self.summary.observe(labels, obs)

class MetricsMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: ASGIApp) -> None:
		super().__init__(app)
		self.request_timing_histogram = Histogram('api_response_time_seconds')

	async def dispatch(self, req: Request, call_next: RequestResponseEndpoint) -> Response:
		start_time = perf_counter()
		res = await call_next(req)
		elapsed_secs = perf_counter() - start_time
		self.request_timing_histogram.observe(
			elapsed_secs,
			method = req.method,
			path = req.url.path,
			status = res.status_code,
		)
		return res
