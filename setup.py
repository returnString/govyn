from setuptools import setup, find_packages

setup(
	name = 'govyn',
	version = '0.1.0',
	author = 'Ruan Pearce-Authers',
	author_email = 'ruanpa@outlook.com',
	description = 'HTTP APIs in typed Python',
	url = 'https://github.com/returnString/govyn',
	packages = find_packages(),
	package_data = {
		'govyn': [ 'py.typed' ],
	},
	zip_safe = False,
	install_requires = [
		'starlette >= 0.13',
		'uvicorn >= 0.11',
		'dacite >= 1.5.1',
		'requests >= 2.24',
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires = '>= 3.8',
)
