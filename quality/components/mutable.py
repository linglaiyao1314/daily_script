import re
import pendulum
import datetime
import decimal

from quality.components.base import Component

__all__ = ["CharStart", "CharEnd", "CharExists", "CharAll",
           "WordStart", "WordEnd", "WordExists",
           "LengthBetween", "TimeBetween"]


class _StringComponent(Component):
    params = ("pattern_str",)

    def __init__(self, pattern_str):
        super().__init__()
        if len(pattern_str) > 1024:
            raise ValueError("Pattern string is too long (> 1024)")
        self.pattern_str = pattern_str
        self.pattern = self.init_pattern()

    def actioning(self, text):
        return bool(re.search(self.pattern, text))


class CharExists(_StringComponent):
    """是否存在某个字母"""

    def __init__(self, pattern_str):
        super().__init__(pattern_str=pattern_str)

    def init_pattern(self):
        return self._cache(self.pattern_str, exact=False)


class CharAll(_StringComponent):
    """是否都为给定的字符"""
    def __init__(self, pattern_str):
        super().__init__(pattern_str)

    def init_pattern(self):
        return self._cache(self.pattern_str, exact=False)

    def actioning(self, text):
        if not re.search(self.pattern, text):
            return False
        count = 0
        for index, char in enumerate(re.finditer(self.pattern, text)):
            if text[index] != char.group():
                return False
            count += 1
        return len(text) == count


class WordExists(_StringComponent):
    """是否存在某个单词"""

    def __init__(self, pattern_str):
        super().__init__(pattern_str=pattern_str)

    def init_pattern(self):
        return self._cache(self.pattern_str)


class CharStart(CharExists):
    """以某些字符开头"""

    def __init__(self, pattern_str=None):
        super().__init__(pattern_str=pattern_str)

    def actioning(self, text):
        return bool(re.match(self.pattern, text))


class CharEnd(CharStart):
    """以某些字符结尾"""

    def __init__(self, pattern_str):
        super().__init__(pattern_str)

    def actioning(self, text):
        text = text[::-1]
        return super().actioning(text)


class WordStart(WordExists):
    def __init__(self, pattern_str):
        super().__init__(pattern_str=pattern_str)

    def actioning(self, text):
        return bool(re.match(self.pattern, text))


class WordEnd(WordStart):
    def __init__(self, pattern_str):
        super().__init__(pattern_str=pattern_str)

    def actioning(self, text):
        return self.pattern_str == text[len(text) - len(self.pattern_str):]


class LengthBetween(Component):
    params = ("left_bound", "right_bound")

    def __init__(self, left_bound=None, right_bound=None):
        super().__init__()
        if left_bound is None and right_bound is None:
            raise ValueError("left_bound and right bound can't be None together!")
        if left_bound is not None and right_bound is not None and left_bound > right_bound:
            raise ValueError("left_bound is greater than right_bound")
        self._left_bound = left_bound
        self._right_bound = right_bound

    def actioning(self, text):
        text_len = len(text)
        if self._right_bound and self._right_bound < text_len:
            return False
        if self._left_bound and self._left_bound > text_len:
            return False
        return True

    @property
    def left_bound(self):
        return self._left_bound

    @property
    def right_bound(self):
        return self._right_bound


class TimeBetween(Component):
    params = ("left_bound", "right_bound")
    fields = {"year", "month", "day", "hour", "minute", "second", "microsecond", "tzinfo"}

    def __init__(self, left_bound=None, right_bound=None):
        super().__init__()
        if left_bound is None:
            self._left_bound = {}
        else:
            self._left_bound = self._make_datetime(left_bound or {})
        if right_bound is None:
            self._right_bound = {}
        else:
            self._right_bound = self._make_datetime(right_bound or {})
        if not self._left_bound and not self._right_bound:
            raise ValueError("left_bound and right bound can't be None together!")
        if self._left_bound and self._right_bound:
            assert self._left_bound <= self._right_bound, ValueError("left bound is greater than right bound!")

    def actioning(self, data):
        t = self._make_datetime(data)
        if self._left_bound and self._left_bound > t:
            return False
        if self._right_bound and self._right_bound < t:
            return False
        return True

    def _make_datetime(self, data):
        try:
            data = decimal.Decimal(data)
        except Exception:
            pass
        if isinstance(data, str):
            data = int(pendulum.parse(data).timestamp())
        elif isinstance(data, dict):
            try:
                data = int(pendulum.datetime(**self._format_pendulum(data)).timestamp())
            except Exception:
                raise ValueError("dict data field value type error!")
        elif isinstance(data, (int, decimal.Decimal, float)):
            pass
        elif isinstance(data, datetime.datetime):
            data = int(data.timestamp())
        else:
            raise ValueError("bound format is not support")
        return data

    def _format_pendulum(self, data):
        data = {field: data[field] for field in self.fields if data.get(field)}
        template = {
            'year': 1900,
            'month': 1,
            'day': 1,
            'hour': 0,
            'minute': 0,
            'second': 0
        }
        _data = {}
        for key in template.keys():
            _data[key] = data.get(key) or template[key]
        return _data

    @property
    def left_bound(self):
        return self._left_bound

    @property
    def right_bound(self):
        return self._right_bound


if __name__ == '__main__':
    print((TimeBetween({"year": 500}, {"year": 2100})).apply("1"))