from django.conf import settings
from django.contrib.sites.requests import RequestSite

from .core import validate_html


class HTMLValidator(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        if not getattr(settings, 'HTMLVALIDATOR_ENABLED', False):
            return response

        if (
            response.status_code == 200 and (
                response['content-type'].startswith('text/html') or
                response['content-type'].startswith('application/xhtml+xml')
            )
        ):
            path = request.path[1:]
            if path.endswith('/'):
                path = path[:-1]

            filename = path.replace('/', '_')
            if not filename:
                # e.g. an error on `/`
                filename = 'index.html'
            if not filename.endswith('.html'):
                filename += '.html'
            filename = '%s-%s' % (RequestSite(request).domain, filename)
            filename = filename.replace(':', '-')  # Windows
            validate_html(
                response.content,
                response['Content-Type'],
                filename,
                ([], request.GET)
            )
        return response

