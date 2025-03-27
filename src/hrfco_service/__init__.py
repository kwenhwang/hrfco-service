from . import server
import asyncio

def main():
    """패키지의 메인 진입점."""
    asyncio.run(server.main())