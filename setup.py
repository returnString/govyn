from setuptools import setup

with open('readme.md', 'r', encoding = 'utf-8') as fh:
	long_description = fh.read()

setup(
	name = 'govyn',
	version = '0.14.0',
	author = 'Ruan Pearce-Authers',
	author_email = 'ruanpa@outlook.com',
	description = 'HTTP APIs in typed Python',
	url = 'https://github.com/returnString/govyn',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	packages = [ 'govyn' ],
	package_data = {
		'govyn': [ 'py.typed' ],
	},
	zip_safe = False,
	install_requires = [
		'starlette >= 0.14',
		'uvicorn >= 0.13',
		'dacite >= 1.5.1',
		'aioprometheus[aiohttp] >= 20.0',
		# not explicit dependencies, but required to avoid build breaks
		'aiohttp >= 3.7',
	],
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires = '>= 3.8',
)
