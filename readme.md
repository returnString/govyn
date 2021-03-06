# govyn
![Tests](https://github.com/returnString/govyn/workflows/Tests/badge.svg) [![PyPI version](https://badge.fury.io/py/govyn.svg)](https://pypi.org/project/govyn) [![codecov](https://codecov.io/gh/returnString/govyn/branch/main/graph/badge.svg)](https://codecov.io/gh/returnString/govyn)

A tiny framework for writing async HTTP APIs in typed Python.

> **govyn** (verb) - ask, inquire, query, question, request ([Cornish Dictionary](https://www.cornishdictionary.org.uk/#govyn))

# Features
- Async everywhere!
- Method params as query string arguments
- Dataclasses as request bodies
- Authentication with principals and privileges
- OpenAPI support with built-in routes:
	- `/openapi/schema`: OpenAPI v3 schema as JSON
	- `/openapi/swagger`: embedded [Swagger UI](https://swagger.io/tools/swagger-ui/) page for testing
	- `/openapi/redoc`: embedded [Redoc](https://redoc.ly/redoc) documentation page
- Prometheus metrics support

# Example
```python
from dataclasses import dataclass
from typing import List
from govyn import run

@dataclass
class AddRequest:
	numbers: List[int]

@dataclass
class Response:
	result: int

class CalculatorAPI:
	# run initialisation tasks, e.g. connecting to a database
	async def startup(self) -> None:
		pass

	# be a good citizen and dispose of things appropriately
	async def shutdown(self) -> None:
		pass

	# get_ methods take a query string
	# callers will receive a 400 Bad Request if they supply invalid values
	async def get_add(self, a: int, b: int) -> Response:
		return Response(a + b)

	# post_ methods take a JSON request body
	# also type-checked according to the dataclass definition
	async def post_add(self, req: AddRequest) -> Response:
		return Response(sum(req.numbers))

run(CalculatorAPI())
```

Try out the built-in Swagger UI on this [example Heroku deployment](https://govyn-demo.herokuapp.com/openapi/swagger), built from source available in the [govyn-demo](https://github.com/returnString/govyn-demo) repository!

Or, run the server locally and hit it with curl:

```bash
> curl "http://localhost/add?a=10&b=32"
{"result": 42}
> curl "http://localhost/add" -d '{ "numbers": [ 1000, 300, 30, 7 ] }'
{"result": 1337}
```

# Installation
```bash
# from PyPI
pip install govyn

# or directly from Git
pip install git+ssh://git@github.com/returnString/govyn.git
```
