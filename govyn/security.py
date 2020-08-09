from typing import List
from dataclasses import dataclass, field

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

@dataclass
class CORSConfig:
	origins: List[str]
	methods: List[str]
	request_headers: List[str]
	response_headers: List[str]
	include_cookies: bool
	max_age_secs: int

def permissive_cors_config() -> CORSConfig:
	return CORSConfig(
		origins = [ '*' ],
		methods = [ '*' ],
		request_headers = [ '*' ],
		response_headers = [ '*' ],
		include_cookies = False,
		max_age_secs = 600,
	)

def cors_middleware_from_config(config: CORSConfig) -> Middleware:
	return Middleware(
		CORSMiddleware,
		allow_origins = config.origins,
		allow_methods = config.methods,
		allow_headers = config.request_headers,
		allow_credentials = config.include_cookies,
		expose_headers = config.response_headers,
	)
