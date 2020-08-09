from typing import Any, Optional, Dict, List

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.types import ASGIApp
import uvicorn

from .route_def import make_route_def
from .schemas import build_schemas
from .swagger import build_swagger_ui
from .endpoint import make_endpoint
from .errors import JSONErrorMiddleware
from .auth import AuthBackend, AuthMiddleware

def create_app(srv: Any, name: Optional[str] = None, auth_backend: Optional[AuthBackend] = None) -> ASGIApp:
	name = name or type(srv).__name__
	route_defs = [ make_route_def(getattr(srv, m)) for m in dir(srv) if not m.startswith('_') and m not in { 'startup', 'shutdown' } ]

	openapi_schemas = build_schemas(route_defs, name, auth_backend)
	swagger_ui = build_swagger_ui(name)

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

	core_app = Starlette(
		routes = [
			Route(r.path, make_endpoint(r), methods = [ r.http_method.upper() ])
			for r in route_defs
		],
		middleware = middleware,
	)

	openapi_app = Starlette(
		routes = [
			Route('/swagger', lambda _: HTMLResponse(swagger_ui)),
			Route('/schema', lambda _: JSONResponse(openapi_schemas)),
		],
	)

	return Starlette(routes = [
		Mount('/openapi', openapi_app),
		Mount('/', core_app),
	], on_startup = startup_funcs, on_shutdown = shutdown_funcs)

def run_app(app: ASGIApp, port: int = 80, host: str = "0.0.0.0") -> None:
	uvicorn.run(app, host = host, port = port)
