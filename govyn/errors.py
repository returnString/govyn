import traceback
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, ClassVar, Optional

from starlette.exceptions import HTTPException
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


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
		try:
			response = await call_next(request)
			return response
		except HTTPError as ex:
			return error_response(ex.code, ex.desc, ex.data)
		except Exception as ex:
			print("Internal Error")
			traceback.print_exc()
			return error_response(500, None, None)
