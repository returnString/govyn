from typing import Dict, Any
from dataclasses import asdict

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from dacite.core import from_dict
from dacite.exceptions import DaciteError

from .route_def import RouteDef, ArgDef

async def query_string_parser(req: Request, args: Dict[str, ArgDef]) -> Dict[str, Any]:
	ret: Dict[str, Any] = dict()
	for var_name, arg_def in args.items():
		value = req.query_params.get(var_name)
		if value is None:
			if not arg_def.optional:
				raise HTTPException(400)
			ret[var_name] = None
		else:
			try:
				ret[var_name] = arg_def.parser(value) # type: ignore
			except ValueError as e:
				raise HTTPException(400, str(e))

	return ret

async def json_body_parser(req: Request, args: Dict[str, ArgDef]) -> Dict[str, Any]:
	json_body = await req.json()
	name = list(args)[0]
	arg_def = args[name]

	try:
		body: Any = from_dict(arg_def.expected_type, json_body)
	except DaciteError as e:
		raise HTTPException(400, str(e))

	return { name: body }

_parser_dict = {
	'get': query_string_parser,
	'post': json_body_parser,
}

def make_endpoint(route: RouteDef) -> Any:
	parser = _parser_dict[route.http_method]

	async def endpoint(req: Request) -> Any:
		args = await parser(req, route.args)
		res = await route.impl(**args)
		return JSONResponse(asdict(res))

	return endpoint
