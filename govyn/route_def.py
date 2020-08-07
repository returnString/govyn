from typing import Any, Union, Dict, Callable
from dataclasses import dataclass

from .errors import BadRequest
from .auth import Principal

_ParserType = Callable[[ str ], Any]

@dataclass
class ArgDef:
	expected_type: type
	optional: bool
	parser: _ParserType

def _parse_bool(x: str) -> bool:
	x = x.lower()
	if x == "true":
		return True
	elif x == "false":
		return False
	raise BadRequest('invalid boolean value')

_parser_overrides: Dict[type, _ParserType] = {
	bool: _parse_bool,
}

def make_arg_def(expected_type: type) -> ArgDef:
	is_optional = getattr(expected_type, '__origin__', None) == Union and getattr(expected_type, '__args__')[1] == type(None)

	if is_optional:
		expected_type = getattr(expected_type, '__args__')[0]

	parser = _parser_overrides.get(expected_type, expected_type)

	return ArgDef(
		expected_type = expected_type,
		optional = is_optional,
		parser = parser,
	)

@dataclass
class RouteDef:
	path: str
	http_method: str
	impl: Callable[..., Any]
	args: Dict[str, ArgDef]
	return_type: type
	requires_principal: bool

def make_route_def(impl: Callable[..., Any]) -> RouteDef:
	name_tokens = impl.__name__.split('_')
	http_method = name_tokens[0]

	input_annotations = impl.__annotations__.copy()
	return_type = input_annotations['return']
	del input_annotations['return']
	requires_principal = input_annotations.get('principal') is not None
	if requires_principal:
		del input_annotations['principal']

	if http_method == 'post':
		if len(input_annotations) != 1:
			raise Exception('POST methods require one argument')

	args = {
		name: make_arg_def(expected_type) for name, expected_type
		in input_annotations.items()
	}

	return RouteDef(
		path = '/' + '_'.join(name_tokens[1:]),
		http_method = http_method,
		impl = impl,
		args = args,
		return_type = return_type,
		requires_principal = requires_principal,
	)
