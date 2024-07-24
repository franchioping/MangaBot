import asyncio

import requests


async def get(*args, **kwargs):
    return await asyncio.to_thread(requests.get, *args, **kwargs)