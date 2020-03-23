import re
from functools import lru_cache


@lru_cache(maxsize=1024)
def pattern_cache(pattern_str, exact=True, escape=True, flags=0):
    """
    :param pattern_str: 原始带匹配字符串
    :param exact: True匹配整个字符串，False匹配字符串中的字符
    :param escape: 是否需要转义，对于一些符号可以设置escape为True
    :param flags:
    re.I(re.IGNORECASE): 忽略大小写（括号内是完整写法，下同）
            M(MULTILINE): 多行模式，改变'^'和'$'的行为
            S(DOTALL): 点任意匹配模式，改变'.'的行为
            L(LOCALE): 使预定字符类 \w \W \b \B \s \S 取决于当前区域设定
            U(UNICODE): 使预定字符类 \w \W \b \B \s \S \d \D 取决于unicode定义的字符属性
            X(VERBOSE): 详细模式。
    :return:
    """
    if not exact:
        mod = "[%s]"
    else:
        mod = "%s"
    if escape:
        pattern = mod % re.escape(pattern_str)
    else:
        pattern = mod % pattern_str
    return re.compile(pattern, flags=flags)


class Component:
    params = ()

    def __init__(self):
        self._cache = pattern_cache
        self.neg = False
        self.pattern = None

    def __and__(self, other_component):
        return AndComponent(self, other_component)

    def __or__(self, other_component):
        return OrComponent(self, other_component)

    def __neg__(self):
        self.neg = not self.neg
        return self

    def __invert__(self):
        return self.__neg__()

    def init_pattern(self) -> str:
        """初始化匹配模式"""
        raise NotImplemented("not implement")

    def actioning(self, text) -> bool:
        return bool(re.search(self.pattern, text))

    def apply(self, text) -> bool:
        if self.neg:
            return not self.actioning(text)
        return self.actioning(text)


class ImmutableComponent(Component):
    def __init__(self):
        super().__init__()
        self.pattern = self._init_pattern()

    def __neg__(self):
        self.neg = not self.neg
        return self

    def _init_pattern(self):
        return self.init_pattern()


class AndComponent(Component):
    def __init__(self, left_component, right_component):
        super().__init__()
        self.left_component = left_component
        self.right_component = right_component

    def apply(self, text):
        if self.left_component.apply(text):
            return self.right_component.apply(text)
        return False

    def __neg__(self):
        self.neg = not self.neg
        self.left_component = -self.left_component
        self.right_component = -self.right_component
        return self


class OrComponent(AndComponent):
    def __init__(self, left_component, right_component):
        super().__init__(left_component, right_component)

    def apply(self, text):
        if self.left_component.apply(text):
            return True
        return self.right_component.apply(text)

    def __neg__(self):
        self.neg = not self.neg
        self.left_component = -self.left_component
        self.right_component = -self.right_component
        return self
