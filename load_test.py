#!/usr/bin/env python3
"""Load Testing for AMOS Brain API

Usage:
    python load_test.py --duration 60 --concurrent 10

Measures:
    - Requests per second
    - Average response time
    - Error rate
"""

import argparse
import asyncio
import time
from statistics import mean, median

import aiohttp

BASE_URL = "http://localhost:5000"


async def make_request(session, endpoint, payload=None):
    """Make a single request and measure time."""
    start = time.time()
    try:
        if payload:
            async with session.post(
                f"{BASE_URL}{endpoint}", json=payload, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                await resp.read()
                status = resp.status
        else:
            async with session.get(
                f"{BASE_URL}{endpoint}", timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                await resp.read()
                status = resp.status

        elapsed = time.time() - start
        return {"status": status, "time": elapsed, "error": None}
    except Exception as e:
        elapsed = time.time() - start
        return {"status": 0, "time": elapsed, "error": str(e)}


async def worker(session, endpoint, payload, requests_queue, results):
    """Worker that makes requests until queue is empty."""
    while True:
        try:
            requests_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        result = await make_request(session, endpoint, payload)
        results.append(result)


async def run_load_test(endpoint, payload, total_requests, concurrent):
    """Run load test with specified parameters."""
    print(f"\n🚀 Load Test: {endpoint}")
    print(f"   Requests: {total_requests}")
    print(f"   Concurrent: {concurrent}")
    print("-" * 50)

    # Create request queue
    queue = asyncio.Queue()
    for _ in range(total_requests):
        queue.put_nowait(1)

    results = []

    # Create session and workers
    async with aiohttp.ClientSession() as session:
        workers = [worker(session, endpoint, payload, queue, results) for _ in range(concurrent)]

        start = time.time()
        await asyncio.gather(*workers)
        total_time = time.time() - start

    # Calculate stats
    success = [r for r in results if r["status"] == 200]
    errors = [r for r in results if r["status"] != 200]
    times = [r["time"] for r in success]

    # Print results
    print("\n📊 Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {len(success)}/{total_requests}")
    print(f"   Error rate: {len(errors)/total_requests*100:.1f}%")

    if times:
        print(f"   RPS: {len(success)/total_time:.1f}")
        print(f"   Avg time: {mean(times)*1000:.0f}ms")
        print(f"   Median time: {median(times)*1000:.0f}ms")
        print(f"   Min time: {min(times)*1000:.0f}ms")
        print(f"   Max time: {max(times)*1000:.0f}ms")

    if errors:
        print("\n⚠️  First 3 errors:")
        for e in errors[:3]:
            print(f"   {e['status']}: {e['error'][:50] if e['error'] else 'No error'}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Load test AMOS Brain API")
    parser.add_argument("--duration", type=int, default=30, help="Test duration in seconds")
    parser.add_argument("--concurrent", type=int, default=5, help="Concurrent requests")
    parser.add_argument("--endpoint", default="/health", help="Endpoint to test")

    args = parser.parse_args()

    # Estimate total requests based on duration
    total_requests = args.duration * args.concurrent

    # Determine payload
    payload = None
    if args.endpoint == "/think":
        payload = {"query": "Load test query", "domain": "general"}
    elif args.endpoint == "/decide":
        payload = {"question": "Load test?", "options": ["A", "B"]}

    print("=" * 50)
    print("AMOS Brain API - Load Test")
    print("=" * 50)

    asyncio.run(run_load_test(args.endpoint, payload, total_requests, args.concurrent))


if __name__ == "__main__":
    main()
