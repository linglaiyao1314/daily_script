"""
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
from aiokafka import AIOKafkaProducer
from aiokafka import AIOKafkaConsumer


loop = asyncio.get_event_loop()


async def consume():
    hosts = "172.31.30.7:9092,172.31.18.18:9092,172.31.26.41:9092".split(",")

    consumer = AIOKafkaConsumer(
        'ireport_luckytime',
        loop=loop,
        group_id="hello",
        bootstrap_servers=",".join(hosts),
        auto_offset_reset="earliest"
    )
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        print("start to consumer...")
        async for msg in consumer:
            try:
                print(msg.value)
            except:
                continue
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


async def send_one():
    producer = AIOKafkaProducer(
        loop=loop,
        bootstrap_servers="bj-ai-kafka-prod-01:9092,bj-ai-kafka-prod-02:9092,bj-ai-kafka-prod-03:9092,bj-ai-kafka-prod-04:9092,bj-ai-kafka-prod-05:9092,bj-ai-kafka-prod-06:9092,bj-ai-kafka-prod-07:9092,bj-ai-kafka-prod-08:9092,bj-ai-kafka-prod-09:9092,bj-ai-kafka-prod-10:9092".split(","))
    await producer.start()
    try:
        print("haha")
        # await producer.send_and_wait("di_apm_common", data.encode())
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

if __name__ == '__main__':
    loop.run_until_complete(consume())
