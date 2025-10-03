from fastapi.openapi.utils import get_openapi
from config.config import config


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )

    # openapi_schema["components"]["securitySchemes"] = {
    #     "BearerAuth": {
    #         "type": "http",
    #         "scheme": "bearer",
    #     },
    #     "CrossToken": {
    #         "type": "apiKey",
    #         "name": "X-Cross-Token",
    #         "in": "header",
    #     },
    #     "TenantId": {
    #         "type":"apiKey",
    #         "name":"X-Tenant-Id",
    #         "in":"header"
    #     }
    # }

    # openapi_schema["security"] = [{"BearerAuth": [], "CrossToken": [], "TenantId": []}]

    # Explicitly set the servers field with the required base path
    openapi_schema["servers"] = [
        {"url": f"/api/{config.app_name.lower()}", "description": "Base path for API"}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
