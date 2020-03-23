import datetime
from functools import partial
from typing import List, Dict
from kafka import KafkaConsumer, TopicPartition
from dataclasses import dataclass


def extract_date(msg):
    pos = msg.find(b"@_receive_at")
    t = msg[pos + 16: pos + 16 + 13]
    date = datetime.datetime.fromtimestamp(int(t.decode()) / 1e3)
    return date


def less_than_detect_func(msg: bytes, bound_date=None):
    if bound_date is None:
        bound_date = datetime.datetime.now()
    date = extract_date(msg)
    return date < bound_date


@dataclass
class PartitionInformation:
    inter: TopicPartition
    start_offset: int
    end_offset: int


class KafkaSimpleStats:
    def __init__(self, detect_func, topic):
        self.topic = topic
        self._func = detect_func
        if self.topic == "ireport_luckytime_pythonsync":
            self.consumer = KafkaConsumer(bootstrap_servers=['192.168.101.63:9092'],
                                          group_id='131',
                                          auto_offset_reset='earliest',
                                          consumer_timeout_ms=10000)
        else:
            self.consumer = KafkaConsumer(bootstrap_servers=['172.31.30.7:9092',
                                                             '172.31.18.18:9092',
                                                             '172.31.26.41:9092'],
                                          group_id='detect_offset',
                                          auto_offset_reset='earliest',
                                          consumer_timeout_ms=10000)
        self._topic_map = {}
        for t in self.consumer.topics():
            self._topic_map.setdefault(t, self._init_partitions(t))

    def _init_partitions(self, topic):
        partition_nums = self.consumer.partitions_for_topic(topic)
        return [TopicPartition(topic, i)
                for i in partition_nums]

    def generate_partitions_information(self, topic) -> Dict[int, PartitionInformation]:
        result = {}
        partitions = self.get_topic_partitions(topic)

        self.consumer.assign(partitions)
        self.consumer.seek_to_beginning(*partitions)
        start_offset = [self.consumer.position(i) for i in partitions]

        self.consumer.assign(partitions)
        self.consumer.seek_to_end(*partitions)
        end_offset = [self.consumer.position(i) for i in partitions]

        for p in partitions:
            result[p.partition] = PartitionInformation(p, start_offset[p.partition], end_offset[p.partition])

        return result

    def get_topic_partitions(self, topic) -> List[TopicPartition]:
        assert self._topic_map[topic] is not None
        return self._topic_map[topic]

    def binary_detect(self, partition: PartitionInformation):
        """
        针对有序kafka数据进行查找
        :param partition:
        :return:
        """
        self.consumer.assign([partition.inter])
        left, right = partition.start_offset, partition.end_offset
        mid = (left + right) // 2
        while left < right:
            print(mid, left, right)
            self.consumer.seek(partition.inter, mid)
            try:
                msg1 = next(self.consumer)
                msg2 = next(self.consumer)
            except StopIteration:
                return mid
            x1 = self._func(msg1.value)
            x2 = self._func(msg2.value)
            # 异或运算
            if x1 ^ x2:
                break
            else:
                # 小于，则增加
                if x1:
                    left = mid + 1
                else:
                    right = mid
            mid = (left + right) // 2
        return mid

    def check(self, partition: PartitionInformation, pos):
        self.consumer.assign([partition.inter])
        self.consumer.seek(partition.inter, pos)
        msg1 = next(self.consumer)
        msg2 = next(self.consumer)
        print(extract_date(msg1.value))
        print(extract_date(msg2.value))

    def run(self):
        info_list = self.generate_partitions_information(self.topic)
        total = 0
        for k, v in info_list.items():
            print("partition is:", k, v.start_offset, v.end_offset)
            self.check(v, v.start_offset)
            self.check(v, v.end_offset - 2)
            total += self.binary_detect(v)
        return total

