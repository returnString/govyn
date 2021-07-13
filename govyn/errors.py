from typing import Any, Optional, ClassVar
from dataclasses import dataclass
from http import HTTPStatus
import traceback

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.exceptions import HTTPException

@dataclass
class HTTPError(HTTPException):
	desc: str
	data: Optional[Any] = None
	code: ClassVar[int]

	def __post_init__(self) -> None:
		super().__init__(self.code, self.desc)

	def as_response(self) -> JSONResponse:
		return error_response(self.code, self.desc, self.data)

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
class NotFound(HTTPError):
	code = 404

@dataclass
class Conflict(HTTPError):
	code = 409

@dataclass
class TooManyRequests(HTTPError):
	code = 429

@dataclass
class InternalServerError(HTTPError):
	code = 500

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
			return e.as_response()
		except Exception as e:
			traceback.print_exc()
			return error_response(500, None, None)
