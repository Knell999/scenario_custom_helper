#!/usr/bin/env python3
"""
비동기 처리 성능 벤치마킹 스크립트
"""

import time
import json
import asyncio
import aiohttp
import requests
from typing import List, Dict, Any
import statistics
from datetime import datetime

class AsyncBenchmark:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_payload = {
            "chapterId": "benchmark-test",
            "story": "[{\"turn_number\":1,\"result\":\"벤치마크 테스트 시나리오입니다.\",\"news\":\"성능 테스트가 진행됩니다.\",\"news_tag\":\"all\",\"stocks\":[{\"name\":\"테스트 주식\",\"risk_level\":\"중위험\",\"description\":\"테스트용 주식입니다.\",\"before_value\":100,\"current_value\":100,\"expectation\":\"테스트 중입니다.\"}]}]",
            "editRequest": "이야기를 더 흥미롭게 만들어주세요."
        }

    async def health_check(self) -> bool:
        """서버 상태 확인"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    return response.status == 200
        except:
            return False

    async def test_async_endpoint(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """비동기 엔드포인트 테스트"""
        start_time = time.time()
        try:
            async with session.post(
                f"{self.base_url}/edit-scenario-async",
                json=self.test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                end_time = time.time()
                return {
                    "success": response.status == 200,
                    "duration": end_time - start_time,
                    "status_code": response.status,
                    "response_size": len(str(result))
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "duration": end_time - start_time,
                "error": str(e)
            }

    def test_sync_endpoint(self) -> Dict[str, Any]:
        """동기 엔드포인트 테스트"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/edit-scenario",
                json=self.test_payload,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            return {
                "success": response.status_code == 200,
                "duration": end_time - start_time,
                "status_code": response.status_code,
                "response_size": len(response.text)
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "duration": end_time - start_time,
                "error": str(e)
            }

    async def concurrent_async_test(self, num_requests: int = 3) -> List[Dict[str, Any]]:
        """동시 비동기 요청 테스트"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.test_async_endpoint(session) for _ in range(num_requests)]
            return await asyncio.gather(*tasks)

    def concurrent_sync_test(self, num_requests: int = 3) -> List[Dict[str, Any]]:
        """동시 동기 요청 테스트 (실제로는 순차 처리)"""
        results = []
        for _ in range(num_requests):
            results.append(self.test_sync_endpoint())
        return results

    async def run_benchmark(self):
        """전체 벤치마크 실행"""
        print("🚀 비동기 처리 성능 벤치마킹 시작")
        print("=" * 50)
        
        # 서버 상태 확인
        print("🔍 서버 상태 확인 중...")
        if not await self.health_check():
            print("❌ 서버가 응답하지 않습니다. 서버를 먼저 시작해주세요.")
            return
        print("✅ 서버 정상 응답")
        
        # 1. 단일 요청 성능 테스트
        print("\n📊 단일 요청 성능 테스트")
        print("-" * 30)
        
        # 비동기 단일 요청
        async with aiohttp.ClientSession() as session:
            async_result = await self.test_async_endpoint(session)
        
        # 동기 단일 요청
        sync_result = self.test_sync_endpoint()
        
        print(f"비동기 처리: {async_result['duration']:.2f}초 ({'성공' if async_result['success'] else '실패'})")
        print(f"동기 처리:   {sync_result['duration']:.2f}초 ({'성공' if sync_result['success'] else '실패'})")
        
        if async_result['success'] and sync_result['success']:
            improvement = ((sync_result['duration'] - async_result['duration']) / sync_result['duration']) * 100
            print(f"성능 개선:   {improvement:+.1f}%")
        
        # 2. 동시 요청 성능 테스트
        print("\n📊 동시 요청 성능 테스트 (3개 요청)")
        print("-" * 30)
        
        # 비동기 동시 요청
        start_time = time.time()
        async_concurrent_results = await self.concurrent_async_test(3)
        async_total_time = time.time() - start_time
        
        # 동기 순차 요청
        start_time = time.time()
        sync_concurrent_results = self.concurrent_sync_test(3)
        sync_total_time = time.time() - start_time
        
        async_success_count = sum(1 for r in async_concurrent_results if r['success'])
        sync_success_count = sum(1 for r in sync_concurrent_results if r['success'])
        
        print(f"비동기 처리: {async_total_time:.2f}초 ({async_success_count}/3 성공)")
        print(f"동기 처리:   {sync_total_time:.2f}초 ({sync_success_count}/3 성공)")
        
        if async_success_count > 0 and sync_success_count > 0:
            concurrent_improvement = ((sync_total_time - async_total_time) / sync_total_time) * 100
            print(f"동시성 개선: {concurrent_improvement:+.1f}%")
        
        # 3. 응답 시간 분석
        print("\n📊 응답 시간 분석")
        print("-" * 30)
        
        if async_success_count > 0:
            async_durations = [r['duration'] for r in async_concurrent_results if r['success']]
            print(f"비동기 평균: {statistics.mean(async_durations):.2f}초")
            print(f"비동기 최소: {min(async_durations):.2f}초")
            print(f"비동기 최대: {max(async_durations):.2f}초")
        
        if sync_success_count > 0:
            sync_durations = [r['duration'] for r in sync_concurrent_results if r['success']]
            print(f"동기 평균:   {statistics.mean(sync_durations):.2f}초")
            print(f"동기 최소:   {min(sync_durations):.2f}초")
            print(f"동기 최대:   {max(sync_durations):.2f}초")
        
        # 4. 시스템 성능 정보
        print("\n📊 시스템 성능 정보")
        print("-" * 30)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/performance") as response:
                    if response.status == 200:
                        perf_data = await response.json()
                        print(f"CPU 사용률: {perf_data['system']['cpu_percent']:.1f}%")
                        print(f"메모리 사용률: {perf_data['system']['memory_percent']:.1f}%")
                        print(f"활성 비동기 작업: {perf_data['async_status']['active_tasks']}")
                        print(f"완료된 작업: {perf_data['async_status']['completed_tasks']}")
        except Exception as e:
            print(f"성능 정보 가져오기 실패: {e}")
        
        print("\n✅ 벤치마킹 완료")
        print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    benchmark = AsyncBenchmark()
    await benchmark.run_benchmark()

if __name__ == "__main__":
    asyncio.run(main())
