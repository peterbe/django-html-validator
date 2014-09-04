from django.conf import settings
from django.contrib.sites.models import RequestSite

from .utils import find_charset_encoding
from .core import validate_html


class HTMLValidator(object):

    def process_response(self, request, response):
        if not getattr(settings, 'HTMLVALIDATOR_ENABLED', False):
            return response

        if (
            response.status_code == 200 and
            response['content-type'].startswith('text/html')
        ):
            encoding = find_charset_encoding(response['Content-Type'])
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
            validate_html(
                response.content,
                encoding,
                filename,
                (request.GET, {})
            )
        return response
