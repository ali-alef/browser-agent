import asyncio
from orchestrator.pipeline import main

async def run():
    await main()

asyncio.run(run())
