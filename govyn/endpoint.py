from typing import Dict, Any, Callable, Awaitable
from dataclasses import asdict, is_dataclass

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from dacite.core import from_dict
from dacite.exceptions import DaciteError

from .route_def import RouteDef, ArgDef
from .errors import BadRequest

def parse_value(arg: ArgDef, var_name: str, str_value: str) -> Any:
	try:
		return arg.parser(str_value) # type: ignore
	except ValueError as e:
		raise BadRequest(f'invalid value for field {var_name} of type {arg.element_type.__name__}: {str(e)}')

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
	json_body = await req.json()
	name = list(args)[0]
	arg_def = args[name]

	try:
		body: Any = from_dict(arg_def.element_type, json_body)
	except DaciteError as e:
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
		return JSONResponse(res)

	return endpoint
