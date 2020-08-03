from typing import Any, Union, Dict, Callable
from dataclasses import dataclass

@dataclass
class ArgDef:
	expected_type: type
	optional: bool

@dataclass
class RouteDef:
	path: str
	http_method: str
	impl: Callable[..., Any]
	args: Dict[str, ArgDef]
	return_type: type

def make_arg_def(expected_type: type) -> ArgDef:
	is_optional = getattr(expected_type, '__origin__', None) == Union and getattr(expected_type, '__args__')[1] == type(None)

	if is_optional:
		expected_type = getattr(expected_type, '__args__')[0]

	return ArgDef(
		expected_type = expected_type,
		optional = is_optional,
	)

def make_route_def(impl: Callable[..., Any]) -> RouteDef:
	name_tokens = impl.__name__.split('_')
	http_method = name_tokens[0]

	input_annotations = impl.__annotations__.copy()
	return_type = input_annotations['return']
	del input_annotations['return']

	if http_method == 'post':
		if len(input_annotations) != 1:
			raise Exception('POST methods require one argument')

	args = { name: make_arg_def(expected_type) for name, expected_type in input_annotations.items() }

	return RouteDef(
		path = '/' + '_'.join(name_tokens[1:]),
		http_method = http_method,
		impl = impl,
		args = args,
		return_type = return_type,
	)
