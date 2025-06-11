"""
시스템 상태 및 관리 UI 컴포넌트
"""
import streamlit as st
from source.utils.error_handler import error_handler, health_checker, NotificationType
from source.utils.performance import performance_monitor
import json
from datetime import datetime

def render_system_status():
    """시스템 상태 표시"""
    st.header("🔧 시스템 상태")
    
    # 상태 체크 실행
    if st.button("🔄 상태 새로고침", type="secondary"):
        health_result = health_checker.run_health_check()
        st.session_state.last_health_check = health_result
    
    # 마지막 상태 체크 결과 표시
    if 'last_health_check' in st.session_state:
        health_result = st.session_state.last_health_check
        
        # 전체 상태
        overall_status = health_result["overall_status"]
        if overall_status == "healthy":
            st.success("✅ 시스템 정상 작동")
        elif overall_status == "warning":
            st.warning("⚠️ 일부 문제 발견")
        else:
            st.error("❌ 시스템 오류 발생")
        
        # 개별 체크 결과
        st.subheader("세부 상태")
        col1, col2 = st.columns(2)
        
        with col1:
            for check_name, result in health_result["checks"].items():
                status_icon = {
                    "healthy": "✅",
                    "warning": "⚠️", 
                    "error": "❌"
                }.get(result["status"], "❓")
                
                st.write(f"{status_icon} **{check_name}**: {result['message']}")
        
        with col2:
            # 성능 정보
            perf_report = performance_monitor.get_performance_report()
            st.write("**성능 정보:**")
            st.json(perf_report)
    
    # 에러 통계
    error_stats = error_handler.get_error_statistics()
    if error_stats["total_errors"] > 0:
        st.subheader("🚨 에러 통계")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 에러", error_stats["total_errors"])
        with col2:
            st.metric("세션 에러", error_stats["session_errors"])
        with col3:
            st.metric("최근 1시간", error_stats["recent_errors"])
        
        if error_stats["common_errors"]:
            st.write("**자주 발생하는 에러:**")
            for error_type, count in error_stats["common_errors"]:
                st.write(f"- {error_type}: {count}회")

def render_admin_panel():
    """관리자 패널"""
    st.header("⚙️ 관리자 패널")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ 세션 초기화"):
            keys_to_clear = ['chat_history', 'current_game_data', 'current_story_name']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            error_handler.show_notification("세션이 초기화되었습니다", NotificationType.SUCCESS)
            st.rerun()
    
    with col2:
        if st.button("📊 에러 로그 초기화"):
            error_handler.clear_error_history()
            if 'error_count' in st.session_state:
                st.session_state.error_count = 0
            error_handler.show_notification("에러 로그가 초기화되었습니다", NotificationType.SUCCESS)
            st.rerun()
    
    with col3:
        if st.button("🔧 강제 재초기화"):
            # 커스터마이저 재초기화
            try:
                from source.components.game_customizer import GameCustomizer
                st.session_state.customizer = GameCustomizer()
                error_handler.show_notification("시스템이 재초기화되었습니다", NotificationType.SUCCESS)
            except Exception as e:
                error_handler.handle_error(e, "시스템 재초기화", "재초기화에 실패했습니다")
    
    # 시스템 정보
    st.subheader("📋 시스템 정보")
    system_info = {
        "현재 시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "세션 키 개수": len(st.session_state.keys()),
        "에러 발생 횟수": st.session_state.get('error_count', 0),
        "마지막 에러": st.session_state.get('last_error_time', "없음")
    }
    
    for key, value in system_info.items():
        st.write(f"**{key}**: {value}")

def render_debug_info():
    """디버깅 정보"""
    st.header("🐛 디버깅 정보")
    
    # 세션 상태 정보
    with st.expander("📊 세션 상태", expanded=False):
        session_data = {}
        for key, value in st.session_state.items():
            if key.startswith('_'):
                continue
            try:
                # JSON 직렬화 가능한지 확인
                json.dumps(str(value))
                session_data[key] = str(value)[:200]  # 길이 제한
            except:
                session_data[key] = f"<{type(value).__name__}>"
        
        st.json(session_data)
    
    # API 설정 정보
    with st.expander("🔑 API 설정", expanded=False):
        from source.utils.config import load_api_key
        api_key = load_api_key()
        st.write(f"**API 키 상태**: {'✅ 설정됨' if api_key else '❌ 없음'}")
        if api_key:
            st.write(f"**API 키 길이**: {len(api_key)}자")
            st.write(f"**API 키 시작**: {api_key[:10]}...")
    
    # 파일 시스템 정보
    with st.expander("📁 파일 시스템", expanded=False):
        import os
        story_dir = "saved_stories"
        if os.path.exists(story_dir):
            files = [f for f in os.listdir(story_dir) if f.endswith('.json')]
            st.write(f"**스토리 파일 개수**: {len(files)}")
            if files:
                st.write("**파일 목록**:")
                for file in files[:10]:  # 최대 10개만 표시
                    st.write(f"- {file}")
        else:
            st.error("스토리 디렉토리가 존재하지 않습니다")
    
    # 성능 정보
    with st.expander("⚡ 성능 정보", expanded=False):
        perf_report = performance_monitor.get_performance_report()
        st.json(perf_report)

def render_help_center():
    """도움말 센터"""
    st.header("❓ 도움말 센터")
    
    # FAQ
    st.subheader("🔍 자주 묻는 질문")
    
    faqs = [
        {
            "question": "스토리가 로드되지 않아요",
            "answer": "1. 스토리 파일이 saved_stories 폴더에 있는지 확인하세요\n2. 파일이 올바른 JSON 형식인지 확인하세요\n3. 시스템 상태에서 파일 시스템을 체크해보세요"
        },
        {
            "question": "AI가 응답하지 않아요",
            "answer": "1. API 키가 올바르게 설정되었는지 확인하세요\n2. 인터넷 연결을 확인하세요\n3. 시스템 상태에서 LLM 모델 상태를 확인하세요"
        },
        {
            "question": "에러가 계속 발생해요",
            "answer": "1. 세션을 초기화해보세요\n2. 브라우저를 새로고침하세요\n3. 관리자 패널에서 강제 재초기화를 시도하세요"
        },
        {
            "question": "스토리 편집이 제대로 안 돼요",
            "answer": "1. 명확하고 구체적인 요청을 해보세요\n2. 한 번에 하나의 요소만 수정 요청하세요\n3. 가이드에 있는 예시를 참고하세요"
        }
    ]
    
    for i, faq in enumerate(faqs, 1):
        with st.expander(f"Q{i}. {faq['question']}"):
            st.write(faq["answer"])
    
    # 문제 해결 가이드
    st.subheader("🛠️ 문제 해결 가이드")
    
    st.write("**일반적인 문제 해결 순서:**")
    st.write("1. 시스템 상태 확인")
    st.write("2. 에러 로그 확인") 
    st.write("3. 세션 초기화")
    st.write("4. 브라우저 새로고침")
    st.write("5. 강제 재초기화")
    
    # 연락처
    st.subheader("📞 지원")
    st.info("추가 도움이 필요하시면 시스템 관리자에게 문의하세요.")

def render_system_management():
    """시스템 관리 통합 UI"""
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 시스템 상태", "⚙️ 관리자", "🐛 디버깅", "❓ 도움말"])
    
    with tab1:
        render_system_status()
    
    with tab2:
        render_admin_panel()
    
    with tab3:
        render_debug_info()
    
    with tab4:
        render_help_center()
