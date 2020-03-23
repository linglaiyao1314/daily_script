import requests
import json
import os
import datetime
import pymysql
import redis
import pandas as pd
from scrapy import Selector
from sqlalchemy import create_engine
from googletrans import Translator


def get_mysql_connect():
    return pymysql.connect(
        host='localhost',  # mysql服务器地址
        port=3306,  # 端口号
        user='root',  # 用户名
        passwd='admin',  # 密码
        db='emoji_fun',  # 数据库名称
        charset='utf8',  # 连接编码，根据需要填写
    )


class EmojiPatch:
    def __init__(self):
        self._translator = Translator()

    @classmethod
    def get_exists_data(cls):
        uri = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8" % ("root", "admin", "localhost", 3306, "emoji_fun")
        engine = create_engine(uri)
        df = pd.read_sql("select * from emoji_info", engine)
        return df

    def run(self):
        data = self.get_exists_data()
        for index, row in data.iterrows():
            # result = self.process_row(row)
            break


    def process_row(self, row):
        tags = row.tags
        trans_res = self._translator.translate(tags, dest="zh-cn", src="en")
        tags_cn = ",".join([i.strip() for i in trans_res.text.split(",")])
        print(tags_cn)
        print(tags_cn.split(","))

if __name__ == '__main__':
    e = EmojiPatch()
    e.run()