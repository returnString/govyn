from typing import Dict, Any, List, Union, Optional, Literal
from dataclasses import is_dataclass, fields
from collections import defaultdict
from enum import Enum
from datetime import datetime, date

from .route_def import RouteDef
from .auth import AuthBackend

_pytype_to_schema_type_lookup = {
	int: 'integer',
	str: 'string',
	float: 'number',
	bool: 'boolean',
	type(None): 'null',
	datetime: 'string',
	date: 'string,'
}

_pytype_string_formats = {
	datetime: 'date-time',
	date: 'date',
}

def pytype_to_schema(py_type: type) -> Dict[str, Any]:
	origin_type = getattr(py_type, '__origin__', None)
	generic_types = getattr(py_type, '__args__', None)

	if not origin_type:
		if is_dataclass(py_type):
			return {
				'type': 'object',
				'properties': { f.name: pytype_to_schema(f.type) for f in fields(py_type) },
			}
	else:
		if origin_type == list:
			return {
				'type': 'array',
				'items': pytype_to_schema(generic_types[0]),
			}
		elif origin_type == dict:
			if generic_types[0] is not str:
				raise Exception('dictionary keys must be strings')

			return {
				'type': 'object',
				'additionalProperties': pytype_to_schema(generic_types[1]),
			}
		elif origin_type == Union:
			return {
				'oneOf': [ pytype_to_schema(t) for t in generic_types ],
			}
		elif origin_type == Literal:
			return {
				'type': _pytype_to_schema_type_lookup[type(generic_types[0])],
				'enum': generic_types,
			}

	return {
		'type': _pytype_to_schema_type_lookup[py_type],
		'format': _pytype_string_formats.get(py_type),
	}

def build_schemas(route_defs: List[RouteDef], api_name: str, auth_backend: Optional[AuthBackend]) -> Dict[str, Any]:
	paths: Dict[str, Any] = defaultdict(dict)
	for route_def in route_defs:
		spec: Any = {
			'summary': route_def.readable_name,
			'description': route_def.doc,
			'responses': {
				'200': {
					'description': 'success',
					'content': {
						'application/json': {
							'schema': pytype_to_schema(route_def.return_type),
						},
					},
				},
			}
		}

		if route_def.http_method == 'get':
			spec['parameters'] = [ {
					'name': arg_name,
					'in': 'query',
					'schema': pytype_to_schema(arg_def.original_type),
					'required': not arg_def.optional,
				}
				for arg_name, arg_def in route_def.args.items()
			]
		else:
			spec['requestBody'] = {
				'required': True,
				'content': {
					'application/json': {
						'schema': pytype_to_schema(list(route_def.args.values())[0].original_type),
					},
				},
			}

		paths[route_def.path][route_def.http_method] = spec

	openapi_spec: Dict[str, Any] = {
		'openapi': '3.0.0',
		'info': {
			'title': api_name,
			'version': '0.1',
		},
		'paths': paths,
		'components': {},
	}

	if auth_backend:
		auth_name, spec = auth_backend.openapi_spec()
		openapi_spec['components']['securitySchemes'] = {
			auth_name: spec,
		}
		openapi_spec['security'] = [
			{ auth_name: [] },
		]

	return openapi_spec
