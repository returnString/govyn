from typing import Any, Optional, ClassVar, Callable, Awaitable
from dataclasses import dataclass
from http import HTTPStatus
import traceback

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

@dataclass
class HTTPError(Exception):
	desc: str
	data: Optional[Any] = None
	code: ClassVar[int]

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

def error_response(code: int, desc: Optional[str], data: Optional[Any]) -> JSONResponse:
	return JSONResponse({
		'error_type': HTTPStatus(code).phrase,
		'error_description': desc,
		'error_data': data,
	}, code)

class JSONErrorMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
		# TODO: logging
		try:
			response = await call_next(request)
			return response
		except HTTPError as e:
			return error_response(e.code, e.desc, e.data)
		except Exception as e:
			traceback.print_exc()
			return error_response(500, None, None)
