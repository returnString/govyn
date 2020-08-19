from typing import Optional, Any

import uvicorn

from .app import create_app
from .auth import AuthBackend
from .security import CORSConfig

def run(
		srv: Any,
		name: Optional[str] = None,
		auth_backend: Optional[AuthBackend] = None,
		cors_config: Optional[CORSConfig] = None,
		port: int = 80,
		metrics_port: int = 5000,
		host: str = "0.0.0.0",
	) -> None:
	app = create_app(srv, name, auth_backend, cors_config, metrics_port)
	uvicorn.run(app, host = host, port = port)
