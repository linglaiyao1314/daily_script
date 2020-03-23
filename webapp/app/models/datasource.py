from sqlalchemy import Column, Integer, ForeignKey, String, Text, Time
from app.db.base_class import Base
from enum import Enum, unique


@unique
class SourceType(Enum):
    mysql = 1
    clickhouse = 2
    hive = 3
    spark = 4


class DataSource(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64))
    # 数据源类型：
    source_type = Column(Integer)
    description = Column(Text)
    host = Column(String(512))
    port = Column(Integer)
    user = Column(String(64))
    password = Column(String(64))
    db_name = Column(String(64))
    # 连接相关参数
    kwargs = Column(Text)
    status = Column(Integer)
    created_at = Column(Time)
    updated_at = Column(Time)
    create_by = Column(Integer)


