import asyncio

sem = asyncio.Semaphore(10)


async def print_num(k: int):
    await sem.acquire()
    print(k, "start")
    await asyncio.sleep(1)
    sem.release()
    print(k, "end")


async def runner():
    await asyncio.gather(*[print_num(k) for k in range(100)])


asyncio.run(runner())
