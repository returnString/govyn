from typing import Any, Optional, ClassVar, Callable, Awaitable
from dataclasses import dataclass
from http import HTTPStatus

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

@dataclass
class HTTPError(Exception):
	desc: str
	data: Optional[Any] = None

@dataclass
class BadRequest(HTTPError):
	code = 400

@dataclass
class Unauthorised(HTTPError):
	code = 401

@dataclass
class Forbidden(HTTPError):
	code = 403

@dataclass
class Conflict(HTTPError):
	code = 409

class JSONErrorMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
		try:
			response = await call_next(request)
			return response
		except HTTPError as e:
			code: int = e.code # type: ignore
			return JSONResponse({
				'error_type': HTTPStatus(code).phrase,
				'error_description': e.desc,
				'error_data': e.data,
			}, code)
