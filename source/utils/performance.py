"""
성능 최적화 유틸리티
"""
import time
import functools
from typing import Any, Callable
import streamlit as st

def cache_result(expire_after: int = 300):
    """결과 캐싱 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Streamlit 세션 상태에서 캐시 확인
            if cache_key in st.session_state:
                cached_time, cached_result = st.session_state[cache_key]
                if time.time() - cached_time < expire_after:
                    return cached_result
            
            # 캐시가 없거나 만료된 경우 실행
            result = func(*args, **kwargs)
            st.session_state[cache_key] = (time.time(), result)
            
            return result
        return wrapper
    return decorator

def optimize_large_content(content: str, max_length: int = 10000) -> str:
    """대용량 콘텐츠 최적화"""
    if len(content) <= max_length:
        return content
    
    # 내용을 요약하거나 제한
    return content[:max_length] + f"\n\n... (총 {len(content):,}자, {max_length:,}자로 제한)"

def batch_process(items: list, batch_size: int = 10):
    """배치 처리"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

class PerformanceMonitor:
    """성능 모니터링"""
    
    def __init__(self):
        self.timings = {}
    
    def start_timer(self, operation: str):
        """타이머 시작"""
        self.timings[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """타이머 종료 및 결과 반환"""
        if operation in self.timings:
            duration = time.time() - self.timings[operation]
            del self.timings[operation]
            return duration
        return 0.0
    
    def get_performance_report(self) -> dict:
        """성능 리포트 생성"""
        return {
            "active_timers": len(self.timings),
            "session_cache_size": len([k for k in st.session_state.keys() if k.startswith("cache_")]),
            "memory_usage": "추정 불가"  # 더 정확한 메모리 사용량은 psutil 필요
        }

# 전역 성능 모니터
performance_monitor = PerformanceMonitor()
