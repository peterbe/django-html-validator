from django.conf import settings
from django.contrib.sites.requests import RequestSite
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


from .core import validate_html


class HTMLValidator(MiddlewareMixin):

    def process_response(self, request, response):
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
