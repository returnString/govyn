def build_redoc_ui(title: str) -> str:
	return f'''
	<html>
	<head>
		<title>ReDoc - {title}</title>
		<meta charset="utf-8"/>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
		</style>
	</head>
	<body>
		<redoc spec-url='/openapi/schema'></redoc>
		<script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
	</body>
	</html>
	'''
