"""
pip install uvloop
pip install tqdm
pip install aiokafka
yum -y install gcc+ gcc-c++
wget https://github.com/google/snappy/releases/download/1.1.3/snappy-1.1.3.tar.gz
tar xzvf snappy-1.1.3.tar.gz
cd snappy-1.1.3
./configure
make
sudo make install
pip install python-snappy
"""
import asyncio
import json
from aiokafka import AIOKafkaConsumer

loop = asyncio.get_event_loop()

topic = "test_ireport_jianduoduo_test"
hosts = "di-inno-kafka01.h.ab1.qttsite.net:9092".split(",")
limit = 1000

async def consume():
    consumer = AIOKafkaConsumer(
        topic,
        loop=loop,
        group_id="count",
        bootstrap_servers=",".join(hosts),
        auto_offset_reset="earliest"
    )
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        count = 0
        async for msg in consumer:
            if count >= limit:
                break
            print(msg)
            count += 1
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


if __name__ == '__main__':
    # loop.run_until_complete(asyncio.gather(consume(), print_stats()))
    loop.run_until_complete(consume())
