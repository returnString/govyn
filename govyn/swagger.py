js = '''
window.onload = function() {
	const ui = SwaggerUIBundle({
		url: "/openapi/schema",
		dom_id: '#swagger-ui',
		deepLinking: true,
		presets: [
			SwaggerUIBundle.presets.apis,
			SwaggerUIStandalonePreset,
		],
		plugins: [
			SwaggerUIBundle.plugins.DownloadUrl,
		],
		layout: "BaseLayout",
	})
	window.ui = ui
}
'''

def build_swagger_ui(title: str) -> str:
	return f'''
	<html>
	<head>
		<meta charset="UTF-8">
		<title>{title}</title>
		<link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.12.1/swagger-ui.css">
	</head>
	<body>

	<div id="swagger-ui"></div>

	<script src="https://unpkg.com/swagger-ui-dist@3.12.1/swagger-ui-standalone-preset.js"></script>
	<script src="https://unpkg.com/swagger-ui-dist@3.12.1/swagger-ui-bundle.js"></script>

	<script>
	{js}
	</script>
	</body>
	</html>
	'''
