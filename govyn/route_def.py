from typing import Any, Union, Dict, Callable, Literal, Set, TypeVar
from dataclasses import dataclass
from datetime import datetime, date

from .errors import BadRequest
from .auth import Principal

_ParserType = Callable[[ str ], Any]

@dataclass
class ArgDef:
	original_type: type
	element_type: type
	optional: bool
	parser: _ParserType
	is_list: bool

def _parse_bool(x: str) -> bool:
	x = x.lower()
	if x == "true":
		return True
	elif x == "false":
		return False
	raise ValueError('expected true or false')

_parser_overrides: Dict[type, _ParserType] = {
	bool: _parse_bool,
	datetime: datetime.fromisoformat,
	date: date.fromisoformat,
}

T = TypeVar('T')
def create_enum_parser(options: Set[T], elem_parser: Callable[[ str ], T]) -> Callable[[ str ], T]:
	def _impl(x: str) -> T:
		if x in options:
			return elem_parser(x)
		else:
			raise ValueError(f'expected one of {options}')
	return _impl

def make_arg_def(original_type: type) -> ArgDef:
	element_type = original_type
	is_optional = getattr(element_type, '__origin__', None) == Union and getattr(element_type, '__args__')[1] == type(None)
	if is_optional:
		element_type = getattr(element_type, '__args__')[0]

	is_list = getattr(element_type, '__origin__', None) == list
	if is_list:
		element_type = getattr(element_type, '__args__')[0]

	parser = _parser_overrides.get(element_type, element_type)

	is_enum = getattr(element_type, '__origin__', None) == Literal
	if is_enum:
		enum_values = getattr(element_type, '__args__')
		element_type = type(enum_values[0])
		enum_values = set(enum_values)
		parser = create_enum_parser(enum_values, _parser_overrides.get(element_type, element_type))
	else:
		enum_values = set()
	
	return ArgDef(
		original_type = original_type,
		element_type = element_type,
		optional = is_optional,
		parser = parser,
		is_list = is_list,
	)

@dataclass
class RouteDef:
	path: str
	http_method: str
	impl: Callable[..., Any]
	args: Dict[str, ArgDef]
	return_type: type
	requires_principal: bool
	readable_name: str
	doc: str

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
		name: make_arg_def(element_type) for name, element_type
		in input_annotations.items()
	}

	return RouteDef(
		path = '/' + '_'.join(name_tokens[1:]),
		http_method = http_method,
		impl = impl,
		args = args,
		return_type = return_type,
		requires_principal = requires_principal,
		readable_name = ' '.join([ s.title() for s in name_tokens[1:] ]),
		doc = getattr(impl, '__doc__'),
	)
