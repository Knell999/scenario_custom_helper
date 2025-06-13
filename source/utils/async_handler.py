"""
비동기 처리 유틸리티 모듈
"""
import asyncio
import streamlit as st
import threading
import time
from typing import Callable, Any, Optional, List, Coroutine
from concurrent.futures import ThreadPoolExecutor
from queue import Queue


def run_async_in_streamlit(coroutine: Coroutine) -> Any:
    """Streamlit에서 비동기 함수를 실행하기 위한 헬퍼 함수"""
    try:
        # 기존 이벤트 루프가 있는지 확인
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 이미 실행 중인 루프가 있다면 새로운 스레드에서 실행
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coroutine)
                finally:
                    new_loop.close()
            
            with ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        else:
            # 루프가 실행 중이 아니라면 직접 실행
            return loop.run_until_complete(coroutine)
    except RuntimeError:
        # 이벤트 루프가 없다면 새로 생성
        return asyncio.run(coroutine)


class AsyncTaskManager:
    """비동기 작업 관리자"""
    
    def __init__(self):
        self.tasks = {}
        self.results = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def run_async_task(self, task_id: str, async_func: Callable, *args, **kwargs):
        """
        비동기 함수를 백그라운드에서 실행합니다.
        
        Args:
            task_id (str): 작업 식별자
            async_func (Callable): 비동기 함수
            *args, **kwargs: 함수 인자
        """
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(async_func(*args, **kwargs))
                self.results[task_id] = {'status': 'completed', 'result': result}
            except Exception as e:
                self.results[task_id] = {'status': 'error', 'error': str(e)}
            finally:
                loop.close()
        
        self.results[task_id] = {'status': 'running'}
        future = self.executor.submit(run_in_thread)
        self.tasks[task_id] = future
        
        return task_id
    
    def get_task_status(self, task_id: str) -> dict:
        """작업 상태를 확인합니다."""
        return self.results.get(task_id, {'status': 'not_found'})
    
    def is_task_completed(self, task_id: str) -> bool:
        """작업이 완료되었는지 확인합니다."""
        result = self.results.get(task_id)
        return result and result['status'] in ['completed', 'error']
    
    def get_task_result(self, task_id: str):
        """작업 결과를 가져옵니다."""
        result = self.results.get(task_id)
        if result and result['status'] == 'completed':
            return result['result']
        elif result and result['status'] == 'error':
            raise Exception(result['error'])
        return None
    
    def cancel_task(self, task_id: str):
        """작업을 취소합니다."""
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
            self.results[task_id] = {'status': 'cancelled'}


class StreamingHandler:
    """스트리밍 처리 핸들러"""
    
    def __init__(self):
        self.queue = Queue()
        self.is_streaming = False
    
    async def stream_callback(self, token: str):
        """스트리밍 토큰 콜백"""
        self.queue.put(token)
    
    def start_streaming(self, container):
        """스트리밍 출력 시작"""
        self.is_streaming = True
        content = ""
        
        while self.is_streaming:
            try:
                token = self.queue.get(timeout=0.1)
                content += token
                container.text(content)
            except:
                time.sleep(0.1)
    
    def stop_streaming(self):
        """스트리밍 중지"""
        self.is_streaming = False


def run_with_progress(task_func: Callable, task_args: tuple = (), 
                     task_kwargs: dict = None, 
                     progress_text: str = "처리 중...",
                     success_text: str = "완료!") -> Any:
    """
    진행률 표시와 함께 작업을 실행합니다.
    
    Args:
        task_func: 실행할 함수
        task_args: 함수 인자
        task_kwargs: 함수 키워드 인자
        progress_text: 진행 중 표시할 텍스트
        success_text: 완료 시 표시할 텍스트
    
    Returns:
        함수 실행 결과
    """
    if task_kwargs is None:
        task_kwargs = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(progress_text)
        progress_bar.progress(30)
        
        # 작업 실행
        result = task_func(*task_args, **task_kwargs)
        
        progress_bar.progress(100)
        status_text.success(success_text)
        
        # 2초 후 진행률 표시 제거
        time.sleep(2)
        progress_bar.empty()
        status_text.empty()
        
        return result
        
    except Exception as e:
        progress_bar.empty()
        status_text.error(f"오류 발생: {str(e)}")
        raise


def create_async_ui_handler():
    """비동기 UI 핸들러 생성"""
    if 'async_manager' not in st.session_state:
        st.session_state.async_manager = AsyncTaskManager()
    
    return st.session_state.async_manager


@st.experimental_fragment(run_every=1.0)
def display_async_status(task_id: str, container):
    """비동기 작업 상태를 주기적으로 업데이트"""
    if 'async_manager' in st.session_state:
        manager = st.session_state.async_manager
        status = manager.get_task_status(task_id)
        
        if status['status'] == 'running':
            container.info("🔄 처리 중...")
        elif status['status'] == 'completed':
            container.success("✅ 완료!")
            return True
        elif status['status'] == 'error':
            container.error(f"❌ 오류: {status.get('error', '알 수 없는 오류')}")
            return True
    
    return False


# 데코레이터
def async_streamlit_task(task_name: str = None):
    """
    Streamlit에서 비동기 작업을 실행하기 위한 데코레이터
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = create_async_ui_handler()
            task_id = task_name or f"task_{int(time.time())}"
            
            # 비동기 작업 시작
            manager.run_async_task(task_id, func, *args, **kwargs)
            
            # 상태 표시 컨테이너
            status_container = st.empty()
            
            # 작업 완료까지 대기
            while not manager.is_task_completed(task_id):
                status_container.info("🔄 처리 중...")
                time.sleep(1)
            
            # 결과 반환
            try:
                result = manager.get_task_result(task_id)
                status_container.success("✅ 완료!")
                time.sleep(1)
                status_container.empty()
                return result
            except Exception as e:
                status_container.error(f"❌ 오류: {str(e)}")
                raise
        
        return wrapper
    return decorator


# 사용 예시
async def example_async_function(prompt: str, delay: int = 3):
    """예시 비동기 함수"""
    await asyncio.sleep(delay)  # 실제 LLM 호출 시뮬레이션
    return f"처리 완료: {prompt}"


def demo_async_usage():
    """비동기 처리 데모"""
    st.title("비동기 처리 데모")
    
    if st.button("비동기 작업 시작"):
        manager = create_async_ui_handler()
        task_id = manager.run_async_task(
            "demo_task",
            example_async_function,
            "테스트 프롬프트",
            delay=5
        )
        
        st.session_state.current_task = task_id
    
    # 진행 상황 표시
    if hasattr(st.session_state, 'current_task'):
        task_id = st.session_state.current_task
        manager = st.session_state.async_manager
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            status_container = st.empty()
        
        with col2:
            if st.button("취소"):
                manager.cancel_task(task_id)
                del st.session_state.current_task
        
        if display_async_status(task_id, status_container):
            # 작업 완료
            try:
                result = manager.get_task_result(task_id)
                st.success(f"결과: {result}")
            except Exception as e:
                st.error(f"오류: {e}")
            finally:
                del st.session_state.current_task
