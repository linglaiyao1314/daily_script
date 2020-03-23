import requests
import json
import os
import datetime
import pymysql
import redis
import pandas as pd
from scrapy import Selector

start_urls = ["https://emojipedia.org/people/",
              "https://emojipedia.org/nature/",
              "https://emojipedia.org/food-drink/",
              "https://emojipedia.org/activity/",
              "https://emojipedia.org/travel-places/",
              "https://emojipedia.org/objects/",
              "https://emojipedia.org/symbols/",
              "https://emojipedia.org/flags/"
              ]


def get_mysql_connect():
    return pymysql.connect(
        host='localhost',  # mysql服务器地址
        port=3306,  # 端口号
        user='root',  # 用户名
        passwd='admin',  # 密码
        db='emoji_fun',  # 数据库名称
        charset='utf8',  # 连接编码，根据需要填写
    )


def insert_mysql(connection, table, row):
    # 获取当天时间
    rows = []
    rows.append((row["name_en"],
                 row["codepoints"],
                 row.get("shortcode", ""),
                 row.get("tags", ""),
                 row["emoji"]
                 ))
    try:
        with connection.cursor() as cursor:
            # 先尝试删除当天存在的记录
            # sql = f"delete from {table} where create >= {date}"
            # cursor.execute(sql)
            # reminder_msg.append(f"删除当天已存在记录: {cursor.rowcount} 条")
            # 插入当天的新纪录
            sql = f"INSERT INTO `{table}` (`name_en`, `codepoints`, `shortcode`, `tags`, `emoji`) " \
                "VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(sql, rows)
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()


redis_server = redis.Redis(host="192.168.13.86")


class SpiderBase:
    name = "base"

    def __init__(self, cookies=None, headers=None):
        if headers is None:
            self._headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
                "Connection": "keep-alive"}
        else:
            self._headers = headers
        self._cookies = cookies
        self._session = requests.Session()

    @property
    def cookies(self):
        return self._cookies

    @property
    def session(self):
        return self._session

    @property
    def headers(self):
        return self._headers

    def crawl(self, **kwargs):
        raise NotImplemented()

    def verify_login_state(self, *args, **kwargs):
        """验证登录状态"""
        raise NotImplemented()

    def make_request(self, methods, url, **kwargs):
        """构造请求，若没给同名参数，默认传cookies和headers"""
        request_func = getattr(self._session, methods, None)
        assert request_func is not None
        request_kwargs = {}
        if self.cookies is not None:
            request_kwargs.update({"cookies": self.cookies})
        if self.headers is not None:
            request_kwargs.update({"headers": self.headers})
        request_kwargs.update(kwargs)
        return request_func(url, **request_kwargs)

    @classmethod
    def create_obj_cookies(cls, cookie_path):
        abs_path = os.path.join(cookie_path, cls.name + "_cookies.json")
        with open(abs_path) as f:
            cookies = json.load(f)
            return cls(cookies=cookies)

    @classmethod
    def get_last_days(cls, days=1, day_format="%Y-%m-%d"):
        today = datetime.datetime.now()
        today = datetime.datetime(year=today.year, month=today.month, day=today.day)
        delta = datetime.timedelta(days=days)
        lastday = today - delta
        return lastday.strftime(day_format)

    @classmethod
    def create_xpath_body(cls, text):
        return Selector(text=text)


class EmojiSpider(SpiderBase):
    emoji_xpath = "//ul[@class='emoji-list']//li/a/@href"
    domain = "https://emojipedia.org"
    start_page = "https://emojipedia.org/emoji"

    def run(self, start_urls):
        count = 0
        s = set()
        with open("links.txt", "w") as f:
            for url in start_urls:
                resp = self.make_request("get", url)
                selector = Selector(response=resp)
                resp = selector.xpath("//ul[@class='emoji-list']//li/a/@href").extract()
                count += len(resp)
                s.update(set(resp))
                f.writelines([i + "\n" for i in resp])
                print(count, len(resp), len(s))

    def extract_items(self):
        prefix = "EMOJI"
        connection = get_mysql_connect()
        with open("links.txt", "r") as f:
            for line in f.readlines()[1500:]:
                if line.strip() == "":
                    continue
                url, codepoints = line.split(" ", 1)
                key = prefix + ":" + url
                print("to process", url, codepoints, redis_server.get(key))
                if redis_server.get(key) == b"2":
                    continue
                resp = self.make_request("get", url)
                result = self.process_item(resp)
                result.update({"codepoints": codepoints})
                if len(result) > 0:
                    redis_server.set(key, "2")
                insert_mysql(connection, "emoji_info", result)
                import time
                time.sleep(0.5)

    def process_item(self, resp):
        res = {}
        selector = Selector(response=resp)
        name = selector.xpath("//h1/text()").extract_first()
        if name:
            res.update({"name_en": name.strip()})
        shortcodes = selector.xpath("//tr//td[@class='shortcodes']/text()").extract_first()
        if shortcodes:
            res.update({"shortcode": shortcodes.strip()})
        tags = selector.xpath("//tr//td[@class='tags']/text()").extract_first()
        if tags:
            res.update({"tags": tags.strip()})
        emoji = selector.xpath("//tr//span[@class='emoji']/text()").extract_first()
        if emoji:
            res.update({"emoji": emoji.encode("utf-8")})
        return res

    def extract_emoji_urls(self):
        resp = self.make_request("get", self.start_page)
        selector = Selector(response=resp)
        urls = selector.xpath('//table[@class="emoji-list"]//td/a/@href').extract()
        codepoints = selector.xpath('//table[@class="emoji-list"]//td[2]/text()').extract()
        with open("links.txt", "w") as f:
            f.writelines([self.domain + url + " " + codepoint + "\n" for url, codepoint in zip(urls, codepoints)])


if __name__ == '__main__':
    s = EmojiSpider()
    # s.extract_item("https://emojipedia.org/older-adult/")
    # s.extract_emoji_urls()
    # s.extract_items()
    with open("cn_links.txt") as f:
        print(len(set(f.readlines())))
