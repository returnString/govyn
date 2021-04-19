from typing import Any, Optional, Dict, List, Protocol

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.types import ASGIApp

from .route_def import make_route_def
from .endpoint import make_endpoint
from .errors import JSONErrorMiddleware
from .auth import AuthBackend, AuthMiddleware
from .security import CORSConfig, permissive_cors_config, cors_middleware_from_config
from .metrics import MetricsMiddleware, MetricsRegistry
from .openapi import openapi_app

def create_app(
		srv: Any,
		name: Optional[str] = None,
		auth_backend: Optional[AuthBackend] = None,
		cors_config: Optional[CORSConfig] = None,
		metrics_port: Optional[int] = None,
	) -> ASGIApp:
	name = name or type(srv).__name__
	cors_config = cors_config or permissive_cors_config()

	http_methods = [ 'get', 'post' ]
	method_prefixes = tuple([ m + '_' for m in http_methods ])
	route_defs = [ make_route_def(getattr(srv, m)) for m in dir(srv) if m in http_methods or m.startswith(method_prefixes) ]

	metrics_registry = getattr(srv, 'metrics', None)
	if not metrics_registry or not isinstance(metrics_registry, MetricsRegistry):
		metrics_registry = MetricsRegistry()

	metrics_registry._const_labels['app'] = name

	async def metrics_async_init() -> None:
		if metrics_port:
			await metrics_registry._prom_svc.start(addr = '0.0.0.0', port = metrics_port)

	startup_funcs = [ metrics_async_init ]
	shutdown_funcs = []

	def _attach_lifecyle_methods(obj: Any) -> None:
		if startup_func := getattr(obj, 'startup', None):
			startup_funcs.append(startup_func)
		if shutdown_func := getattr(obj, 'shutdown', None):
			shutdown_funcs.append(shutdown_func)

	_attach_lifecyle_methods(srv)

	middleware = [ Middleware(JSONErrorMiddleware) ]
	if auth_backend:
		middleware.append(Middleware(AuthMiddleware, auth_backend = auth_backend, metrics_registry = metrics_registry))
		_attach_lifecyle_methods(auth_backend)

	core_app = Starlette(
		routes = [
			Route(r.path, make_endpoint(r), methods = [ r.http_method.upper() ])
			for r in route_defs
		],
		middleware = middleware,
	)

	health_app = Starlette(
		routes = [
			Route('/check', lambda _: JSONResponse({}))
		]
	)

	return Starlette(
		routes = [
			Mount('/openapi', openapi_app(name, route_defs, auth_backend)),
			Mount('/health', health_app),
			Mount('/', core_app),
		],
		on_startup = startup_funcs,
		on_shutdown = shutdown_funcs,
		middleware = [
			Middleware(MetricsMiddleware, metrics_registry = metrics_registry),
			cors_middleware_from_config(cors_config),
		],
	)
