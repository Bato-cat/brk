import asyncio
import aiohttp
import random
from fake_useragent import UserAgent
from datetime import datetime

# AWS-specific optimizations
AWS_IP_ROTATION = True  # Set to False if not using multiple EC2 instances
REQUEST_TIMEOUT = 15
MAX_RETRIES = 5

async def blockscan_check_balance():
    # Enhanced headers with rotating user agents
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

    # AWS IP rotation simulation
    if AWS_IP_ROTATION:
        headers['X-Forwarded-For'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

    for attempt in range(MAX_RETRIES):
        try:
            # Randomized delay between attempts (3-15 seconds)
            delay = random.uniform(3, 15) if attempt > 0 else 0
            await asyncio.sleep(delay)

            # Configure session with timeout and TCP keepalive
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)

            async with aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=connector
            ) as session:
                url = 'https://blockscan.com/Address/0x73af3bcf944a6559933396c1577b257e2054d935'
                
                # Make request with randomized TLS fingerprint
                async with session.get(url) as resp:
                    # Verify response status
                    if resp.status != 200:
                        print(f"{datetime.now()} - Attempt {attempt + 1}: Status {resp.status}")
                        continue
                        
                    data = await resp.text()
                    coins = any(f'title="${i}' in data for i in range(1, 10))
                    
                    print(f"{datetime.now()} - {'Check for coins' if coins else 'No coins'}")
                    return coins

        except Exception as e:
            print(f"{datetime.now()} - Attempt {attempt + 1} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                print(f"{datetime.now()} - Max retries reached")
                return False

async def main():
    result = await blockscan_check_balance()
    # For AWS Lambda integration:
    # return {'statusCode': 200, 'body': json.dumps({'result': result})}

if __name__ == "__main__":
    for x in range(5):
    	asyncio.run(main())