import re

_charset_regex = re.compile('charset=([\w-]+)')
def find_charset_encoding(content_type, default='utf-8'):
    try:
        found = _charset_regex.findall(content_type)
        if found and found[0]:
            return found[0]
    except IndexError:
        pass

    return default
