import re

from quality.components.base import ImmutableComponent

__all__ = ["ChineseExists", "LinkExists", "TagExists"]


class ChineseExists(ImmutableComponent):
    def __init__(self):
        super().__init__()

    def init_pattern(self):
        return self._cache("[\u4e00-\u9fa5]", exact=True, escape=False)


class LinkExists(ImmutableComponent):
    params = ("only",)

    def __init__(self, only=False):
        self._only = only
        super().__init__()
        # 只有链接

    def init_pattern(self):
        if not self.only:
            return self._cache(
                r'(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)', exact=True, escape=False, flags=re.IGNORECASE)
        else:
            return self._cache(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', exact=True, escape=False, flags=re.IGNORECASE)

    @property
    def only(self):
        return self._only


class TagExists(ImmutableComponent):
    def __init__(self):
        super().__init__()

    def init_pattern(self):
        return self._cache("""</?\w+((\s+\w+(\s*=\s*(?:".*?"|'.*?'|[\^'">\s]+))?)+\s*|\s*)/?>""",
                           exact=True,
                           escape=False)
