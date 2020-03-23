
class StringList(object):
    """判断list是否符合要求：
    1、 检查是否为空
    2、 是否存在空字符串串
    3、 检查是否存在重复
    4、 是否存在None
    """

    @classmethod
    def apply(cls, data):
        if not isinstance(data, list):
            return False
        elements = set(data)
        if len(elements) <= 0:
            return False
        if len(elements) != len(data):
            return False
        for elem in elements:
            if len(elem) <= 0:
                return False
            if elem is None:
                return False
        else:
            return True


