from typing import Optional, Any, Dict, Union, Awaitable, Callable, Sequence, Iterator
from dataclasses import dataclass
from time import perf_counter
from contextlib import contextmanager

from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import aioprometheus

Observation = Union[float, int]
LabelValue = Union[str, int]

@dataclass
class LabelUpdater:
	_labels: Dict[str, LabelValue]

	def update(self, **labels: LabelValue) -> None:
		self._labels = { **self._labels, **labels }

@dataclass
class Counter:
	_counter: aioprometheus.Counter

	def inc(self, **labels: LabelValue) -> None:
		self._counter.inc(labels)

	def add(self, val: int, **labels: LabelValue) -> None:
		self._counter.add(labels, val)

@dataclass
class Gauge:
	_gauge: aioprometheus.Gauge

	def set(self, val: Observation, **labels: LabelValue) -> None:
		self._gauge.set(labels, val)

	def inc(self, **labels: LabelValue) -> None:
		self._gauge.inc(labels)

@dataclass
class Histogram:
	_histogram: aioprometheus.Histogram

	def observe(self, obs: Observation, **labels: LabelValue) -> None:
		self._histogram.observe(labels, obs)

	@contextmanager
	def observe_time(self, **labels: LabelValue) -> Iterator[LabelUpdater]:
		start_time = perf_counter()
		label_updater = LabelUpdater(labels)
		yield label_updater
		elapsed_secs = perf_counter() - start_time
		self.observe(elapsed_secs, **label_updater._labels)

class MetricsRegistry:
	def __init__(self) -> None:
		self._prom_svc = aioprometheus.Service()
		self._const_labels: Dict[str, LabelValue] = {}
	
	def counter(self, name: str, desc: str = '') -> Counter:
		counter = aioprometheus.Counter(name, desc, self._const_labels)
		ret = Counter(counter)
		self._prom_svc.register(counter)
		return ret

	def histogram(self, name: str, desc: str = '', buckets: Sequence[float] = aioprometheus.Histogram.DEFAULT_BUCKETS) -> Histogram:
		histogram = aioprometheus.Histogram(name, desc, self._const_labels, buckets = buckets)
		ret = Histogram(histogram)
		self._prom_svc.register(histogram)
		return ret

	def gauge(self, name: str, desc: str = '') -> Gauge:
		gauge = aioprometheus.Gauge(name, desc, self._const_labels)
		ret = Gauge(gauge)
		self._prom_svc.register(gauge)
		return ret

class MetricsMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: ASGIApp, metrics_registry: MetricsRegistry) -> None:
		super().__init__(app)
		self.request_timing_histogram = metrics_registry.histogram('api_response_time_seconds')

	async def dispatch(self, req: Request, call_next: RequestResponseEndpoint) -> Response:
		with self.request_timing_histogram.observe_time(method = req.method, path = req.url.path) as labels:
			res = await call_next(req)
			labels.update(status = res.status_code)

		return res
