"""
비동기 처리 데모 애플리케이션

이 파일은 LLM API의 비동기 처리 기능을 시연합니다.
uv pip install로 설치된 패키지들을 사용합니다.
"""
import streamlit as st
import asyncio
import time
from typing import List, Dict
import json

# 로컬 모듈 임포트
from source.components.game_customizer import GameCustomizer
from source.utils.async_handler import AsyncTaskManager, run_async_in_streamlit
from source.models.llm_handler import (
    initialize_llm_async, 
    generate_game_data_async,
    generate_multiple_scenarios_async
)


def main():
    st.set_page_config(
        page_title="🚀 비동기 LLM 처리 데모",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 비동기 LLM 처리 데모")
    st.markdown("---")
    
    # 사이드바 - 데모 선택
    st.sidebar.title("📋 데모 메뉴")
    demo_type = st.sidebar.selectbox(
        "데모 유형 선택",
        [
            "1️⃣ 기본 비동기 처리",
            "2️⃣ 배치 병렬 처리", 
            "3️⃣ 스트리밍 처리",
            "4️⃣ 기존 스토리 비동기 수정"
        ]
    )
    
    if demo_type == "1️⃣ 기본 비동기 처리":
        demo_basic_async()
    elif demo_type == "2️⃣ 배치 병렬 처리":
        demo_batch_processing()
    elif demo_type == "3️⃣ 스트리밍 처리":
        demo_streaming()
    elif demo_type == "4️⃣ 기존 스토리 비동기 수정":
        render_async_story_modification()


def demo_basic_async():
    """기본 비동기 처리 데모"""
    st.header("1️⃣ 기본 비동기 처리")
    st.markdown("비동기 방식으로 LLM API를 호출하여 더 나은 사용자 경험을 제공합니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 설정")
        prompt = st.text_area(
            "프롬프트 입력",
            value="간단한 모험 게임 스토리를 JSON 형태로 만들어주세요.",
            height=100
        )
        
        if st.button("🚀 비동기 실행", type="primary"):
            if prompt.strip():
                demo_async_generation(prompt)
            else:
                st.warning("프롬프트를 입력해주세요.")
    
    with col2:
        st.subheader("📊 비교")
        st.info("""
        **동기 처리 vs 비동기 처리**
        
        ✅ **비동기 처리 장점:**
        - UI가 블록되지 않음
        - 진행 상황 실시간 표시
        - 여러 작업 동시 처리 가능
        - 사용자가 다른 작업 수행 가능
        
        ❌ **동기 처리 단점:**
        - UI 완전 정지
        - 응답을 기다려야 함
        - 멀티태스킹 불가능
        """)


def demo_async_generation(prompt: str):
    """비동기 생성 실행"""
    # 진행률 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    result_container = st.empty()
    
    async def async_task():
        try:
            # LLM 초기화
            status_text.info("🔧 LLM 모델을 초기화하는 중...")
            progress_bar.progress(0.2)
            
            llm = await initialize_llm_async()
            
            # 생성 시작
            status_text.info("🎯 스토리를 생성하는 중...")
            progress_bar.progress(0.5)
            
            result, metadata = await generate_game_data_async(prompt, llm)
            
            # 완료
            status_text.success("✅ 생성 완료!")
            progress_bar.progress(1.0)
            
            return result, metadata
            
        except Exception as e:
            status_text.error(f"❌ 오류 발생: {str(e)}")
            return None, {"error": str(e)}
    
    # 비동기 실행
    start_time = time.time()
    result, metadata = run_async_in_streamlit(async_task())
    end_time = time.time()
    
    # 결과 표시
    if result:
        with result_container.container():
            st.success(f"🎉 완료! (소요시간: {end_time - start_time:.2f}초)")
            
            # 결과 탭
            tab1, tab2 = st.tabs(["📖 생성된 스토리", "🔍 메타데이터"])
            
            with tab1:
                if isinstance(result, dict):
                    st.json(result)
                else:
                    st.write(result)
            
            with tab2:
                st.json(metadata)


def demo_batch_processing():
    """배치 병렬 처리 데모"""
    st.header("2️⃣ 배치 병렬 처리")
    st.markdown("여러 프롬프트를 동시에 병렬로 처리하여 처리 시간을 단축합니다.")
    
    # 프롬프트 입력
    st.subheader("📝 배치 프롬프트 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_prompts = st.slider("동시 처리할 프롬프트 수", 2, 5, 3)
        max_concurrent = st.slider("최대 동시 실행 수", 1, 5, 3)
    
    with col2:
        st.info(f"""
        **설정 정보:**
        - 총 프롬프트: {num_prompts}개
        - 최대 동시 실행: {max_concurrent}개
        - 예상 처리 시간: 단축됨 ⚡
        """)
    
    # 프롬프트 입력 필드
    prompts = []
    for i in range(num_prompts):
        prompt = st.text_input(
            f"프롬프트 {i+1}",
            value=f"주제 {i+1}에 관한 짧은 게임 스토리를 만들어주세요.",
            key=f"prompt_{i}"
        )
        prompts.append(prompt)
    
    if st.button("🚀 배치 실행", type="primary"):
        if all(p.strip() for p in prompts):
            demo_batch_execution(prompts, max_concurrent)
        else:
            st.warning("모든 프롬프트를 입력해주세요.")


def demo_batch_execution(prompts: List[str], max_concurrent: int):
    """배치 실행 데모"""
    # 진행률 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    async def batch_task():
        try:
            # LLM 초기화
            status_text.info("🔧 LLM 모델 초기화 중...")
            progress_bar.progress(0.1)
            
            llm = await initialize_llm_async()
            
            # 배치 처리
            status_text.info(f"🎯 {len(prompts)}개 프롬프트를 병렬 처리 중...")
            
            results = await generate_multiple_scenarios_async(
                prompts, 
                llm, 
                max_concurrent=max_concurrent
            )
            
            status_text.success("✅ 모든 작업 완료!")
            progress_bar.progress(1.0)
            
            return results
            
        except Exception as e:
            status_text.error(f"❌ 배치 처리 중 오류: {str(e)}")
            return []
    
    # 실행 시간 측정
    start_time = time.time()
    results = run_async_in_streamlit(batch_task())
    end_time = time.time()
    
    # 결과 표시
    if results:
        with results_container.container():
            st.success(f"🎉 배치 처리 완료! (총 소요시간: {end_time - start_time:.2f}초)")
            
            # 결과를 각각 표시
            for i, (result, metadata) in enumerate(results):
                with st.expander(f"📖 결과 {i+1}", expanded=True):
                    if result and "error" not in result:
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.json(result)
                        
                        with col2:
                            st.caption("메타데이터:")
                            st.json(metadata)
                    else:
                        st.error(f"오류: {result.get('error', '알 수 없는 오류')}")


def demo_streaming():
    """스트리밍 처리 데모"""
    st.header("3️⃣ 스트리밍 처리")
    st.markdown("실시간으로 생성되는 내용을 바로 확인할 수 있습니다.")
    
    # 설정
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 설정")
        prompt = st.text_area(
            "스트리밍 프롬프트",
            value="상세한 판타지 모험 게임 스토리를 JSON 형태로 만들어주세요. 캐릭터, 설정, 퀘스트를 포함해주세요.",
            height=120
        )
        
        if st.button("🌊 스트리밍 시작", type="primary"):
            if prompt.strip():
                demo_streaming_execution(prompt)
            else:
                st.warning("프롬프트를 입력해주세요.")
    
    with col2:
        st.subheader("💡 스트리밍 장점")
        st.info("""
        **실시간 피드백:**
        - 즉시 결과 확인 가능
        - 진행 상황 실시간 표시
        - 더 나은 사용자 경험
        - 긴 콘텐츠도 지루하지 않음
        """)


def demo_streaming_execution(prompt: str):
    """스트리밍 실행 데모"""
    st.subheader("🌊 스트리밍 결과")
    
    # 스트리밍 컨테이너
    streaming_container = st.empty()
    status_container = st.empty()
    
    try:
        status_container.info("🌊 스트리밍을 시작합니다...")
        
        # 스트리밍 실행 
        async def streaming_task():
            from source.models.llm_handler import generate_game_data_stream
            llm = await initialize_llm_async()
            return await generate_game_data_stream(prompt, streaming_container, llm)
        
        result, metadata = run_async_in_streamlit(streaming_task())
        
        status_container.success("✅ 스트리밍 완료!")
        
        # 메타데이터 표시
        with st.expander("🔍 생성 정보"):
            st.json(metadata)
            
    except Exception as e:
        status_container.error(f"❌ 스트리밍 중 오류: {str(e)}")


def render_async_story_modification():
    """비동기 스토리 수정 UI"""
    st.title("🚀 비동기 스토리 수정")
    
    # 세션 상태 초기화
    if 'customizer' not in st.session_state:
        st.session_state.customizer = GameCustomizer()
    
    customizer = st.session_state.customizer
    
    # 입력 폼
    with st.form("async_modification_form"):
        story_name = st.selectbox(
            "수정할 스토리 선택",
            ["magic_kingdom", "three_little_pigs", "foodtruck_kingdom", "moonlight_thief"]
        )
        
        user_request = st.text_area(
            "수정 요청사항",
            placeholder="예: 주인공을 여성으로 바꿔주세요",
            height=100
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sync_submit = st.form_submit_button("동기 처리", type="secondary")
        
        with col2:
            async_submit = st.form_submit_button("비동기 처리", type="primary")
        
        with col3:
            stream_submit = st.form_submit_button("스트리밍 처리", type="secondary")
    
    # 동기 처리
    if sync_submit and user_request:
        with st.spinner("동기 처리 중..."):
            start_time = time.time()
            result, metadata = customizer.modify_existing_story(story_name, user_request)
            end_time = time.time()
            
            if result:
                st.success(f"✅ 동기 처리 완료! ({end_time - start_time:.2f}초)")
                st.json(result)
            else:
                st.error(f"❌ 오류: {metadata.get('error', '알 수 없는 오류')}")
    
    # 비동기 처리
    if async_submit and user_request:
        async_manager = create_async_ui_handler()
        
        # 비동기 작업 시작
        task_id = async_manager.run_async_task(
            f"modify_{story_name}_{int(time.time())}",
            customizer.modify_existing_story_async,
            story_name,
            user_request
        )
        
        st.session_state.current_async_task = task_id
        st.session_state.task_start_time = time.time()
        st.rerun()
    
    # 스트리밍 처리
    if stream_submit and user_request:
        st.subheader("🔄 스트리밍 결과")
        streaming_container = st.empty()
        
        try:
            result, metadata = customizer.modify_story_with_streaming(
                story_name, 
                user_request, 
                streaming_container
            )
            
            if result:
                st.success("✅ 스트리밍 처리 완료!")
                st.json(result)
            else:
                st.error(f"❌ 오류: {metadata.get('error', '알 수 없는 오류')}")
        except Exception as e:
            st.error(f"스트리밍 처리 중 오류: {e}")
    
    # 비동기 작업 상태 표시
    if hasattr(st.session_state, 'current_async_task'):
        task_id = st.session_state.current_async_task
        start_time = st.session_state.task_start_time
        
        st.subheader("📊 비동기 작업 상태")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            status_container = st.empty()
        
        with col2:
            if st.button("❌ 취소"):
                async_manager = st.session_state.async_manager
                async_manager.cancel_task(task_id)
                del st.session_state.current_async_task
                del st.session_state.task_start_time
                st.rerun()
        
        # 경과 시간 표시
        elapsed_time = time.time() - start_time
        st.metric("경과 시간", f"{elapsed_time:.1f}초")
        
        # 상태 확인
        if display_async_status(task_id, status_container):
            # 작업 완료
            async_manager = st.session_state.async_manager
            
            try:
                result, metadata = async_manager.get_task_result(task_id)
                total_time = time.time() - start_time
                
                if result:
                    st.success(f"✅ 비동기 처리 완료! (총 {total_time:.2f}초)")
                    st.json(result)
                else:
                    st.error(f"❌ 오류: {metadata.get('error', '알 수 없는 오류')}")
            
            except Exception as e:
                st.error(f"결과 가져오기 실패: {e}")
            
            finally:
                # 정리
                del st.session_state.current_async_task
                del st.session_state.task_start_time


def render_batch_processing():
    """배치 처리 UI"""
    st.title("📦 배치 처리")
    
    if 'customizer' not in st.session_state:
        st.session_state.customizer = GameCustomizer()
    
    customizer = st.session_state.customizer
    
    st.write("여러 스토리를 한 번에 수정할 수 있습니다.")
    
    # 배치 작업 설정
    num_tasks = st.slider("동시 처리할 작업 수", 1, 5, 2)
    
    modifications = []
    for i in range(num_tasks):
        st.subheader(f"작업 {i+1}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            story_name = st.selectbox(
                f"스토리 {i+1}",
                ["magic_kingdom", "three_little_pigs", "foodtruck_kingdom", "moonlight_thief"],
                key=f"story_{i}"
            )
        
        with col2:
            request = st.text_input(
                f"요청사항 {i+1}",
                placeholder="수정 요청...",
                key=f"request_{i}"
            )
        
        if story_name and request:
            modifications.append({
                'story_name': story_name,
                'request': request,
                'chat_history': []
            })
    
    if st.button("🚀 배치 처리 시작", disabled=len(modifications) == 0):
        if modifications:
            with st.spinner(f"배치 처리 중... ({len(modifications)}개 작업)"):
                try:
                    results = customizer.modify_multiple_stories_async(modifications)
                    
                    st.success(f"✅ 배치 처리 완료! ({len(results)}개 결과)")
                    
                    # 결과 표시
                    for i, result in enumerate(results):
                        with st.expander(f"결과 {i+1}: {result['story_name']}"):
                            if result['success']:
                                st.success("성공")
                                if 'data' in result:
                                    st.json(result['data'])
                            else:
                                st.error(f"실패: {result.get('error', '알 수 없는 오류')}")
                
                except Exception as e:
                    st.error(f"배치 처리 중 오류: {e}")


def render_performance_comparison():
    """성능 비교 UI"""
    st.title("⚡ 성능 비교")
    
    if 'customizer' not in st.session_state:
        st.session_state.customizer = GameCustomizer()
    
    customizer = st.session_state.customizer
    
    st.write("동기 vs 비동기 처리 성능을 비교해보세요.")
    
    # 테스트 설정
    test_story = st.selectbox(
        "테스트 스토리",
        ["magic_kingdom", "three_little_pigs", "foodtruck_kingdom"]
    )
    
    test_request = st.text_input(
        "테스트 요청",
        value="주인공의 이름을 '알렉스'로 바꿔주세요"
    )
    
    if st.button("🏁 성능 테스트 시작"):
        if test_story and test_request:
            results = {}
            
            # 동기 처리 테스트
            with st.spinner("동기 처리 테스트 중..."):
                start_time = time.time()
                sync_result, sync_metadata = customizer.modify_existing_story(
                    test_story, test_request
                )
                sync_time = time.time() - start_time
                results['sync'] = {
                    'time': sync_time,
                    'success': sync_result is not None,
                    'result': sync_result
                }
            
            # 비동기 처리 테스트
            with st.spinner("비동기 처리 테스트 중..."):
                async_manager = create_async_ui_handler()
                
                start_time = time.time()
                task_id = async_manager.run_async_task(
                    "performance_test",
                    customizer.modify_existing_story_async,
                    test_story,
                    test_request
                )
                
                # 완료까지 대기
                while not async_manager.is_task_completed(task_id):
                    time.sleep(0.1)
                
                async_time = time.time() - start_time
                
                try:
                    async_result, async_metadata = async_manager.get_task_result(task_id)
                    results['async'] = {
                        'time': async_time,
                        'success': async_result is not None,
                        'result': async_result
                    }
                except Exception as e:
                    results['async'] = {
                        'time': async_time,
                        'success': False,
                        'error': str(e)
                    }
            
            # 결과 표시
            st.subheader("📊 성능 비교 결과")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "동기 처리 시간",
                    f"{results['sync']['time']:.2f}초",
                    delta=None
                )
                if results['sync']['success']:
                    st.success("✅ 성공")
                else:
                    st.error("❌ 실패")
            
            with col2:
                st.metric(
                    "비동기 처리 시간",
                    f"{results['async']['time']:.2f}초",
                    delta=f"{results['async']['time'] - results['sync']['time']:.2f}초"
                )
                if results['async']['success']:
                    st.success("✅ 성공")
                else:
                    st.error("❌ 실패")
            
            # 개선 정도 계산
            if results['sync']['success'] and results['async']['success']:
                improvement = ((results['sync']['time'] - results['async']['time']) / results['sync']['time']) * 100
                if improvement > 0:
                    st.success(f"🚀 비동기 처리가 {improvement:.1f}% 더 빠름!")
                else:
                    st.info(f"⚡ 동기 처리가 {abs(improvement):.1f}% 더 빠름")


def main():
    """메인 비동기 처리 데모"""
    st.set_page_config(
        page_title="비동기 처리 데모",
        page_icon="🚀",
        layout="wide"
    )
    
    st.sidebar.title("🚀 비동기 처리 데모")
    
    page = st.sidebar.selectbox(
        "페이지 선택",
        ["스토리 수정", "배치 처리", "성능 비교"]
    )
    
    if page == "스토리 수정":
        render_async_story_modification()
    elif page == "배치 처리":
        render_batch_processing()
    elif page == "성능 비교":
        render_performance_comparison()


if __name__ == "__main__":
    main()
