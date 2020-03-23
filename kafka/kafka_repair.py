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
import tqdm
from aiokafka import AIOKafkaProducer
from aiokafka import AIOKafkaConsumer


def init_producer(loop):
    producer = AIOKafkaProducer(
        loop=loop,
        bootstrap_servers="bj-ai-kafka-prod-01:9092,bj-ai-kafka-prod-02:9092,bj-ai-kafka-prod-03:9092,bj-ai-kafka-prod-04:9092,bj-ai-kafka-prod-05:9092,bj-ai-kafka-prod-06:9092,bj-ai-kafka-prod-07:9092,bj-ai-kafka-prod-08:9092,bj-ai-kafka-prod-09:9092,bj-ai-kafka-prod-10:9092".split(","))
    return producer


def init_consumer(loop):
    hosts = """us-bp-kafka-prod-01:9092,us-bp-kafka-prod-02:9092,us-bp-kafka-prod-03:9092""".split(",")

    consumer = AIOKafkaConsumer(
        'ireport_luckytime',
        loop=loop,
        group_id="hello",
        bootstrap_servers=",".join(hosts),
        auto_offset_reset="earliest"
    )
    return consumer


class RepairBase:
    def __init__(self,
                 position,
                 loop: asyncio.AbstractEventLoop = None,
                 producer_topic="ireport_luckytime_pythonsync",
                 concurrency=1,
                 debug=False):
        import time
        time.sleep(position + 1)
        self.loop = loop or asyncio.get_event_loop()
        self.producer = init_producer(loop)
        self.consumer = init_consumer(loop)
        self.topic = producer_topic
        self.output_queue = asyncio.Queue(maxsize=10240)
        self.tqdm_bar = tqdm.tqdm(desc=f"{self.__class__.__name__}_{position}", position=position + 1)
        self.concurrency = concurrency
        self.done_tasks = 0
        self.debug = debug
        self.stats = {}

    async def retry_producer(self):
        self.producer = init_producer(self.loop)
        await self.producer.start()

    async def retry_consumer(self):
        self.consumer = init_consumer(self.loop)
        await self.consumer.start()

    async def run_produce_task(self, task_num):
        processed = 0
        try:
            await self.producer.start()
        except Exception as e:
            print("producer error", e)
        try:
            while True:
                try:
                    row = await self.output_queue.get()
                    if row is None:
                        continue
                    else:
                        await self.producer.send_and_wait(self.topic, row)
                        processed += 1
                    self.tqdm_bar.update(1)
                    self.stats.update({
                        f"task_{task_num}": processed
                    })
                except Exception as e:
                    print(e)
                    await asyncio.sleep(1)
                    continue
        except Exception as e:
            await self.retry_producer()

    async def enqueue(self):
        await self.consumer.start()
        print("consumer started!!!")
        try:
            async for msg in self.consumer:
                while True:
                    try:
                        await self.output_queue.put(msg.value)
                    except Exception as e:
                        print(e)
                        await asyncio.sleep(1)
                        continue
                    else:
                        break
        except Exception as e:
            print("to retry consumer", e)
            await self.retry_consumer()

    async def display_stats(self):
        while True:
            await self.debug_info()
            await asyncio.sleep(60)

    async def go(self):
        return asyncio.gather(*[self.run_produce_task(i+1)
                                for i in range(self.concurrency)])

    def run(self):
        tasks = [
            self.go(),
            self.enqueue(),
            # self.display_stats()
        ]
        self.loop.run_until_complete(asyncio.gather(*tasks))

    async def debug_info(self):
        import pprint
        pprint.pprint(self.stats)


def sub_loop(number):
    import uvloop
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(RepairBase(number, loop=loop, concurrency=12).run())


async def run(executor, number):
    tasks = [asyncio.get_event_loop().run_in_executor(executor, sub_loop, i) for i in range(number)]
    await asyncio.wait(tasks)

if __name__ == '__main__':
    import sys
    from concurrent.futures import ProcessPoolExecutor
    number = int(sys.argv[1])
    executor = ProcessPoolExecutor(
        max_workers=number,
    )
    asyncio.get_event_loop().run_until_complete(run(executor, number))



