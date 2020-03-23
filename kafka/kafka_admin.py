import asyncio

from aiokafka import AIOKafkaClient


loop = asyncio.get_event_loop()


async def send_one():
    client = AIOKafkaClient(
        loop=loop, bootstrap_servers='192.168.13.163:9092')
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait("report_apm", str("test").encode())
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

if __name__ == '__main__':
    loop.run_until_complete(send_one())
