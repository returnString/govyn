import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum, EnumMeta
from typing import Any, Awaitable, Callable, Dict

from dacite.config import Config
from dacite.core import from_dict
from dacite.exceptions import DaciteError
from starlette.requests import Request
from starlette.responses import Response

from .errors import BadRequest
from .route_def import ArgDef, RouteDef


def default_json_ser(obj: Any) -> Any:
	if isinstance(obj, (datetime, date)):
		return obj.isoformat()
	if isinstance(obj, Enum):
		return obj.value

	raise TypeError(f'type {type(obj)} is not serializable')

class GovynJSONResponse(Response):
	media_type = 'application/json'

	def render(self, content: Any) -> bytes:
		return json.dumps(
			content,
			ensure_ascii = False,
			allow_nan = False,
			indent = None,
			separators = (',', ':'),
			default = default_json_ser,
		).encode('utf-8')

def parse_value(arg: ArgDef, var_name: str, str_value: str) -> Any:
	try:
		return arg.parser(str_value)
	except ValueError as e:
		base_err = f'invalid value for field {var_name} of type {arg.element_type.__name__}:'
		if isinstance(arg.element_type, EnumMeta):
			raise BadRequest(f'{base_err} Must be one of {[e.value for e in arg.element_type]}') # type: ignore
		raise BadRequest(f'{base_err}: {str(e)}')

async def query_string_parser(req: Request, args: Dict[str, ArgDef]) -> Dict[str, Any]:
	ret: Dict[str, Any] = dict()
	for var_name, arg_def in args.items():
		if arg_def.is_list:
			ret[var_name] = [ parse_value(arg_def, var_name, v) for v in req.query_params.getlist(var_name) ]
		else:
			value = req.query_params.get(var_name)
			if value is None:
				if not arg_def.optional:
					raise BadRequest(f'missing required field: {var_name}')
				ret[var_name] = None
			else:
				ret[var_name] = parse_value(arg_def, var_name, value)
	return ret

async def json_body_parser(req: Request, args: Dict[str, ArgDef]) -> Dict[str, Any]:
	try:
		json_body = await req.json()
	except json.JSONDecodeError:
		raise BadRequest('Request body is not valid JSON')

	name = list(args)[0]
	arg_def = args[name]
	try:
		body: Any = from_dict(arg_def.element_type, json_body, Config(type_hooks = {
			datetime: datetime.fromisoformat,
			date: date.fromisoformat
		}, cast=[Enum]))
	except (DaciteError, ValueError) as e:
		raise BadRequest(str(e))

	return { name: body }

_parser_dict = {
	'get': query_string_parser,
	'post': json_body_parser,
}

def make_endpoint(route: RouteDef) -> Callable[[ Request ], Awaitable[Response]]:
	parser = _parser_dict[route.http_method]

	async def endpoint(req: Request) -> Response:
		args = await parser(req, route.args)
		if route.requires_principal:
			args['principal'] = req.state.principal
		res = await route.impl(**args)
		if is_dataclass(res):
			res = asdict(res)
		return GovynJSONResponse(res)

	return endpoint
