from typing import Any, Optional

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from .route_def import make_route_def
from .schemas import build_schemas
from .endpoint import make_endpoint

def run(srv: Any, name: Optional[str] = None) -> None:
	route_defs = [ make_route_def(getattr(srv, m)) for m in dir(srv) if not m.startswith('_') and m not in { 'startup', 'shutdown' } ]

	openapi_schemas = build_schemas(route_defs, api_name = name or type(srv).__name__)
	core_routes: Any = [
		Route('/schema', lambda _: JSONResponse(openapi_schemas))
	]

	startup_func = getattr(srv, 'startup', None)
	shutdown_func = getattr(srv, 'shutdown', None)
	startup_funcs = [ startup_func ] if startup_func else []
	shutdown_funcs = [ shutdown_func ] if shutdown_func else []

	app = Starlette(routes = core_routes + [
		Route(r.path, make_endpoint(r), methods = [ r.http_method.upper() ])
		for r in route_defs
	], on_startup = startup_funcs, on_shutdown = shutdown_funcs)

	uvicorn.run(app, host = "0.0.0.0", port = 80)
