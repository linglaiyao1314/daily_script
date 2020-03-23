"""
参考string.py复制黏贴:
whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
"""
# punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
# printable = digits + ascii_letters + punctuation + whitespace
import string
# =========================
# default const value
# =========================
start_punctuation = {'~', '!', '@', '#', '$', '%', '^', '&', '*', ')', '_', '-', '+', '=', ']', '}', '|', '\\', '?',
                     '/', '<', '>', '"', "'", ":", ";", '.', ','}
end_punctuation = start_punctuation - {'!', '"', "'", ";", "."}

CN_PUNCTUATION = "".join(["”", "“", "‘", "’", "”",
                          "‘", "…", "—", "’",
                          "！", "￥", "『", "【", "（", "）",
                          "】", "』", "》", "、", "：", "；",
                          "，", "。", "？", "《", "～"])

FULL_PUNCTUATION = string.punctuation + CN_PUNCTUATION
NAME_PUNCTUATION = "".join(list(set(list(string.punctuation)) - {"&"})) + CN_PUNCTUATION
DEFAULT_NAME_START_PUNCTUATION = "".join(start_punctuation) + CN_PUNCTUATION
DEFAULT_NAME_END_PUNCTUATION = "".join(end_punctuation) + CN_PUNCTUATION
