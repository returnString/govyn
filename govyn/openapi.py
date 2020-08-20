from typing import List, Optional

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route

from .schemas import build_schemas
from .route_def import RouteDef
from .auth import AuthBackend

def build_swagger_ui(title: str) -> str:
	return f'''
	<html>
	<head>
		<meta charset="UTF-8">
		<title>{title}</title>
		<link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.12.1/swagger-ui.css">
	</head>
	<body>

	<div id="swagger-ui"></div>

	<script src="https://unpkg.com/swagger-ui-dist@3.12.1/swagger-ui-standalone-preset.js"></script>
	<script src="https://unpkg.com/swagger-ui-dist@3.12.1/swagger-ui-bundle.js"></script>

	<script>
	window.onload = function() {{
		const ui = SwaggerUIBundle({{
			url: "schema",
			dom_id: '#swagger-ui',
			deepLinking: true,
			presets: [
				SwaggerUIBundle.presets.apis,
				SwaggerUIStandalonePreset,
			],
			plugins: [
				SwaggerUIBundle.plugins.DownloadUrl,
			],
			layout: "BaseLayout",
		}})
		window.ui = ui
	}}
	</script>
	</body>
	</html>
	'''

def build_redoc_ui(title: str) -> str:
	return f'''
	<html>
	<head>
		<title>ReDoc - {title}</title>
		<meta charset="utf-8"/>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
		</style>
	</head>
	<body>
		<redoc spec-url='schema'></redoc>
		<script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
	</body>
	</html>
	'''

def openapi_app(
		title: str,
		route_defs: List[RouteDef],
		auth_backend: Optional[AuthBackend],
	) -> Starlette:
	swagger_ui = build_swagger_ui(title)
	redoc_ui = build_redoc_ui(title)

	openapi_schemas = build_schemas(route_defs, title, auth_backend)

	return Starlette(
		routes = [
			Route('/schema', lambda _: JSONResponse(openapi_schemas)),
			Route('/swagger', lambda _: HTMLResponse(swagger_ui)),
			Route('/redoc', lambda _: HTMLResponse(redoc_ui)),
		],
	)
