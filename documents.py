from flask_swagger_ui import get_swaggerui_blueprint

BASE_DOCUMENT_URL = "/docs"
BASE_API_URL = "/static/"

default = get_swaggerui_blueprint(
    BASE_DOCUMENT_URL,
    BASE_API_URL+"default.json",
    config={
        'app_name': 'MIC',
        "info": {
            "title": "MIC API",
            "description": "MIC API",
        }
    },
    blueprint_name="default"
)
