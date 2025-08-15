import asyncio
import aiohttp
import random
from fake_useragent import UserAgent
from datetime import datetime
import os  # Added for port binding

# AWS-specific optimizations (disable if not needed)
AWS_IP_ROTATION = False  # Disabled for Render
REQUEST_TIMEOUT = 15
MAX_RETRIES = 5

async def blockscan_check_balance():
    headers = {
        'User-Agent': UserAgent().random,
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }

    if AWS_IP_ROTATION:  # Now disabled by default
        headers['X-Forwarded-For'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

    for attempt in range(MAX_RETRIES):
        try:
            delay = random.uniform(3, 15) if attempt > 0 else 0
            await asyncio.sleep(delay)

            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)

            async with aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=connector
            ) as session:
                url = 'https://blockscan.com/Address/0x73af3bcf944a6559933396c1577b257e2054d935'
                
                async with session.get(url) as resp:
                    if resp.status != 200:
                        print(f"{datetime.now()} - Attempt {attempt + 1}: Status {resp.status}")
                        continue
                        
                    data = await resp.text()
                    coins = any(f'title="${i}' in data for i in range(1, 10))
                    print(f"{datetime.now()} - {'Coins found' if coins else 'No coins'}")
                    return coins

        except Exception as e:
            print(f"{datetime.now()} - Attempt {attempt + 1} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                print(f"{datetime.now()} - Max retries reached")
                return False

async def run_worker():
    """Continuous worker for Render background service"""
    while True:
        await blockscan_check_balance()
        await asyncio.sleep(60)  # Check every 60 seconds

def start_server():
    """Dummy HTTP server to satisfy Render's port binding (optional)"""
    from aiohttp import web
    async def handle(request):
        return web.Response(text="Worker is running")
    
    app = web.Application()
    app.router.add_get('/', handle)
    return app

if __name__ == "__main__":
    # Render-compatible execution
    if os.environ.get('RENDER'):
        # Option 1: Run as background worker (no port binding needed)
        print("Starting as background worker...")
        asyncio.run(run_worker())
        
        # Option 2: Run with HTTP server (if deploying as web service)
        # app = start_server()
        # web.run_app(app, port=int(os.environ.get('PORT', 8000)), host='0.0.0.0')
    else:
        # Local execution (testing)
        for x in range(5):
            asyncio.run(main())