from typing import Any, Optional, Dict, List

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.types import ASGIApp
import uvicorn

from .route_def import make_route_def
from .schemas import build_schemas
from .endpoint import make_endpoint
from .errors import JSONErrorMiddleware
from .auth import AuthBackend, AuthMiddleware

def create_app(srv: Any, name: Optional[str] = None, auth_backend: Optional[AuthBackend] = None) -> ASGIApp:
	route_defs = [ make_route_def(getattr(srv, m)) for m in dir(srv) if not m.startswith('_') and m not in { 'startup', 'shutdown' } ]

	openapi_schemas = build_schemas(route_defs, api_name = name or type(srv).__name__)
	core_routes: Any = [
		Route('/openapi/schema', lambda _: JSONResponse(openapi_schemas))
	]

	startup_funcs = []
	shutdown_funcs = []

	def _attach_lifecyle_methods(obj: Any) -> None:
		if startup_func := getattr(obj, 'startup', None):
			startup_funcs.append(startup_func)
		if shutdown_func := getattr(obj, 'shutdown', None):
			shutdown_funcs.append(shutdown_func)
	
	_attach_lifecyle_methods(srv)

	middleware: Any = [ Middleware(JSONErrorMiddleware) ]
	if auth_backend:
		middleware.append(Middleware(AuthMiddleware, auth_backend = auth_backend))
		_attach_lifecyle_methods(auth_backend)

	app = Starlette(routes = core_routes + [
		Route(r.path, make_endpoint(r), methods = [ r.http_method.upper() ])
		for r in route_defs
	], on_startup = startup_funcs, on_shutdown = shutdown_funcs, middleware = middleware)

	return app

def run_app(app: ASGIApp, port: int = 80, host: str = "0.0.0.0") -> None:
	uvicorn.run(app, host = host, port = port)
