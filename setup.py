from setuptools import setup

setup(
	name = 'govyn',
	description = 'HTTP APIs in typed Python',
	packages = [ 'govyn' ],
	package_data = {
		'govyn': [ 'py.typed' ],
	},
	zip_safe = False,
	install_requires = [
		'starlette >= 0.13',
		'uvicorn >= 0.11',
		'dacite >= 1.5.1',
		'requests >= 2.24'
	]
)
