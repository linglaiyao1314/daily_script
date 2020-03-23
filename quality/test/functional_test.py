import unittest

from quality.components.immutable import *
from quality.components.mutable import *
from quality.patterns import *


class TestMutableComponent(unittest.TestCase):
    def setUp(self):
        self.verbosity = 2

    def test_char_exists(self):
        self.assertTrue(CharExists("135").apply("1234567890"))
        self.assertFalse((~CharExists("135")).apply("1234567890"))

    def test_char_start_end(self):
        # 以hello之中的一个字符开头
        self.assertTrue(CharStart("hello").apply("hi"))
        # 以hello之中的一个字符开头, aeiou中的一个字符结尾
        self.assertTrue((CharStart("hello") & CharEnd("aeiou")).apply("hi"))

    def test_complex_rule(self):
        # 以abc中的某个单词开头且包含字符串blockchain且结尾不为n
        rule = CharStart("abc") & WordExists("blockchain") & (~CharEnd("n"))
        self.assertFalse(rule.apply("apple blockchain"))
        self.assertTrue(rule.apply("apple blockchain orange"))
        # 判断满足rule的情况下,长度是否在某个范围
        rule = rule & LengthBetween(10, 20)
        self.assertTrue(rule.apply("apple blockchain box"))
        self.assertFalse(rule.apply("apple blockchain banana water"))

    def test_word_exists(self):
        self.assertTrue(WordExists("[hello]").apply("[hello] world!"))
        self.assertFalse(WordExists("[hello]").apply("hello world!"))

    def test_length(self):
        # true
        self.assertTrue(LengthBetween(1, 2).apply("1"))
        self.assertTrue(LengthBetween(2, 2).apply("12"))
        # false
        self.assertFalse(LengthBetween(1, 2).apply("123"))
        # raise
        self.assertRaises(ValueError, LengthBetween, 3, 2)
        self.assertRaises(ValueError, LengthBetween)

    def test_time(self):
        import time
        import datetime
        # true
        self.assertTrue(TimeBetween({"year": 2015}).apply(time.time()))
        self.assertTrue(TimeBetween(time.time(), time.time() + 100).apply(time.time()))
        self.assertTrue(TimeBetween(datetime.datetime.now(), {"year": 2019}).apply(str(time.time() + 360000)))
        # # false
        self.assertFalse(TimeBetween(datetime.datetime.now(), time.time() + 360000).apply(
            datetime.datetime(year=2017, month=12, day=16)))
        # # raise
        self.assertRaises(ValueError, TimeBetween)


class TestImmutableComponent(unittest.TestCase):
    def test_chinese_rule(self):
        self.assertTrue(ChineseExists().apply("你好, wrold"))
        self.assertFalse(ChineseExists().apply("hello world"))
        self.assertTrue(ChineseExists().apply("hello 你 world"))

    def test_tag_rule(self):
        self.assertTrue(LinkExists().apply("href = 'https://www.xxx.com'"))
        self.assertFalse(LinkExists().apply("<a>haha</a>"))
        self.assertFalse(LinkExists().apply("<a>haha</a>"))
        self.assertFalse(LinkExists().apply("href='hello'"))
        self.assertTrue(TagExists().apply("<br/>"))
        self.assertTrue(TagExists().apply("<1>"))


class TestMoney(unittest.TestCase):
    def setUp(self):
        self.pt = Money()

    def test_symbol_start(self):
        self.assertTrue(self.pt.apply("124.1"))
        self.assertTrue(self.pt.apply("$ 1234"))
        self.assertTrue(self.pt.apply("USD 12341"))
        self.assertTrue(self.pt.apply("EUR 123.41224"))
        self.assertTrue(self.pt.apply("CNY 0.4"))

    def test_error(self):
        self.assertFalse(self.pt.apply("$USD 123..41"))
        self.assertFalse(self.pt.apply("1.24.1"))
        self.assertFalse(self.pt.apply("AAA 124.1"))


class TestPattern(unittest.TestCase):
    def test_title(self):
        self.assertTrue(Title.apply("hello"))
        self.assertTrue(Title.apply("(hello"))

    def test_link(self):
        self.assertFalse(Link.apply("http://www.patsnap.com~~~"))
        self.assertTrue(Link.apply("http://www.patsnap.com"))


class TestCombination(unittest.TestCase):
    def test_c(self):
        self.assertTrue((CharStart("123") | WordStart("abc")).apply("abc"))
        self.assertTrue((CharStart("123") | WordStart("abc")).apply("1abc"))
        self.assertFalse((CharStart("123") | WordStart("abc")).apply("4abc"))

    def test_cc(self):
        comp = WordStart("apple") & WordEnd("pen") & CharExists("y")
        self.assertTrue(comp.apply("apple y pen"))
        self.assertFalse(comp.apply("apple n pen"))

        comp2 = WordStart("orange") & WordEnd("car")
        comp3 = comp | comp2

        self.assertFalse(comp3.apply("orange car x"))
        self.assertFalse(comp3.apply("apple pen"))
        self.assertTrue(comp3.apply("orange car"))
        self.assertTrue(comp3.apply("apple y pen"))


if __name__ == '__main__':
    unittest.main()
