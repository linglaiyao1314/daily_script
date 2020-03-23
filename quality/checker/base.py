from collections import namedtuple


def is_empty(value):
    """验证是否值是否为空
    1.验None
    2.验实现了__len__方法的对象
    """
    if value is None:
        return True
    try:
        return len(value) == 0
    except:
        return False


# 状态boolean, 字段验证错误error_field, 交叉验证错误error_cross
LazyCheckResult = namedtuple("LazyCheckResult", ["status", "error_field", "error_cross"])


class BaseHealthCheck:
    # 独立且必须有的字段
    MUST_REQUIRE_FIELD_SET = set()
    # 联合判断的字段,必须包含其中一个[(f1, f2, f3), (f4, f5)]
    REQUIRE_ONE_FIELD_GROUPS = []

    @classmethod
    def required(cls, data=None):
        """验证data是否None"""
        return True if data else False

    @classmethod
    def required_one(cls, *args):
        """验证多个data是否存在一个不为None"""
        return any(cls.required(arg) for arg in args)

    @classmethod
    def validate(cls, data: dict) -> (bool, str):
        requred_validated = set()
        validate_funcs = {
            k: getattr(cls, k) for k in dir(cls) if k.startswith("valid_") and getattr(cls, k, None)
        }
        for field_group in cls.REQUIRE_ONE_FIELD_GROUPS:
            fields = [data.get(i, None) for i in field_group]
            if not cls.required_one(*fields):
                return LazyCheckResult(False, None, "RequireFieldMissing")
        for field in data.keys():
            if field in cls.MUST_REQUIRE_FIELD_SET:
                if is_empty(data[field]):
                    return LazyCheckResult(False, field, None)
                requred_validated.add(field)
            valid_func_name = 'valid_{}'.format(field)
            func = validate_funcs.pop(valid_func_name, None)
            if not func:
                continue
            result = func(**data)
            if result:
                continue
            else:
                return LazyCheckResult(False, field, None)
        if len(requred_validated) != len(cls.MUST_REQUIRE_FIELD_SET):
            return LazyCheckResult(False, None, "RequireFieldMissing")
        return LazyCheckResult(True, None, None)
