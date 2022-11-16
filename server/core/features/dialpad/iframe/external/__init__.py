"""A module which defines external blueprint.

External blueprint handles requests that requires any type of interaction with external integration.

If external blueprint enabled through ENABLE_EXTERNAL, this blueprint will be loaded and added
to sanic app.

IntegrationClient needs to be implemented to be able to successfully load this blueprint.
If it's not implemented, server would raise ImproperlyConfigured error.
"""
