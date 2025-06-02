"""
정보 탭 UI 컴포넌트
"""
import streamlit as st
import json


def render_info_tabs():
    """정보 탭 렌더링"""
    st.markdown("---")
    
    # 탭으로 구분된 추가 정보
    info_tab1, info_tab2, info_tab3, info_tab4 = st.tabs(["ℹ️ 사용 방법", "📊 통계", "🎯 팁", "🔧 설정"])
    
    with info_tab1:
        render_usage_info()
    
    with info_tab2:
        render_statistics()
    
    with info_tab3:
        render_tips()
    
    with info_tab4:
        render_settings()


def render_usage_info():
    """사용 방법 정보 렌더링"""
    col_help1, col_help2 = st.columns(2)
    
    with col_help1:
        st.markdown("""
        ### 🎯 투자 교육 챗봇 사용법
        
        1. **학습 목표 선택**: 왼쪽 사이드바에서 배우고 싶은 투자 방식을 선택하세요
        2. **스토리 선택**: 마법 왕국, 푸드트럭 왕국, 달빛 도둑 중 하나를 선택하세요
        3. **투자 질문**: 채팅창에 투자 관련 질문이나 요청을 입력하세요
        4. **결과 확인**: 오른쪽에서 투자 개념이 포함된 맞춤 스토리를 확인하세요
        
        ### 💡 투자 학습 예시
        - **안정형**: "안전한 투자 방법을 알려줘"
        - **분산투자**: "포트폴리오를 어떻게 구성하나요?"
        - **매매 타이밍**: "언제 사고 팔지 어떻게 정하나요?"
        - **성장형**: "높은 수익을 얻는 방법을 배우고 싶어"
        """)
    
    with col_help2:
        st.markdown("""
        ### 🔍 고급 기능
        
        - **🧠 의도 분석**: AI가 요청의 의도를 자동으로 파악합니다
        - **✅ 품질 검증**: 생성된 스토리의 품질을 자동으로 검증합니다
        - **💡 개선 제안**: AI가 추가 개선 방향을 제안합니다
        - **⭐ 평가 시스템**: 스토리를 평가하고 피드백을 제공할 수 있습니다
        - **💾 스토리 관리**: 저장, 불러오기, 삭제 기능을 제공합니다
        - **📄 내보내기**: JSON 파일로 다운로드하여 다른 용도로 사용할 수 있습니다
        """)


def render_statistics():
    """통계 정보 렌더링"""
    # 세션 통계
    if hasattr(st.session_state, 'chat_history'):
        total_messages = len(st.session_state.chat_history)
        user_messages = len([msg for role, msg in st.session_state.chat_history if role == "user"])
        ai_messages = len([msg for role, msg in st.session_state.chat_history if role == "assistant"])
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("💬 총 대화 수", total_messages)
        
        with col_stat2:
            st.metric("👤 사용자 메시지", user_messages)
        
        with col_stat3:
            st.metric("🤖 AI 응답", ai_messages)
        
        with col_stat4:
            if st.session_state.current_game_data:
                try:
                    data_size = len(st.session_state.current_game_data)
                    st.metric("📊 데이터 크기", f"{data_size} bytes")
                except:
                    st.metric("📊 데이터 크기", "N/A")
            else:
                st.metric("📊 데이터 크기", "0 bytes")
    
    # 저장된 스토리 통계
    if hasattr(st.session_state, 'story_manager'):
        saved_stories = st.session_state.story_manager.get_saved_stories()
        st.subheader("📚 저장된 스토리 통계")
        
        if saved_stories:
            scenario_counts = {}
            total_size = 0
            
            for story in saved_stories:
                scenario = story["metadata"].get("scenario_type", "알 수 없음")
                scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
                total_size += story["size"]
            
            col_saved1, col_saved2 = st.columns(2)
            
            with col_saved1:
                st.metric("📖 총 저장된 스토리", len(saved_stories))
                st.metric("💾 총 데이터 크기", f"{total_size:,} bytes")
            
            with col_saved2:
                st.write("**시나리오별 분포:**")
                for scenario, count in scenario_counts.items():
                    st.write(f"• {scenario}: {count}개")
        else:
            st.info("저장된 스토리가 없습니다.")


def render_tips():
    """팁 정보 렌더링"""
    st.markdown("""
    ### 💡 효과적인 투자 학습 방법
    
    #### 🎯 구체적인 질문하기
    - "투자가 뭐야?" → "안전한 투자 방법을 알려줘"
    - "돈을 어떻게 모으지?" → "분산투자의 장점을 설명해줘"
    
    #### 📈 투자 방식별 학습 포인트
    - **안정형**: 리스크 관리, 안전자산의 중요성
    - **분산투자**: 포트폴리오 구성, 위험 분산의 원리
    - **매매 타이밍**: 시장 분석, 감정 조절의 중요성
    - **성장형**: 장기 투자, 기업 분석 기법
    
    #### 👶 연령별 학습 조절
    - "유치원생도 이해할 수 있게" - 매우 쉬운 단어 사용
    - "초등학생 수준으로" - 적절한 복잡도 유지
    - "좀 더 자세히" - 고급 개념까지 포함
    
    #### 🔄 반복 학습 방법
    - 같은 개념을 다른 스토리로 학습
    - 난이도를 점진적으로 높여가며 반복
    - 실생활 예시와 연결하여 이해도 향상
    """)


def render_settings():
    """설정 정보 렌더링"""
    st.markdown("""
    ### 🔧 고급 설정 및 문제 해결
    
    #### ⚙️ 환경 설정
    - **API 키**: `.env` 파일에 `OPENAI_API_KEY=your_api_key` 형태로 설정
    - **모델 설정**: `utils/config.py`에서 GPT 모델 및 매개변수 조정 가능
    - **저장 위치**: 기본적으로 `saved_stories` 폴더에 저장됨
    
    #### 🐛 문제 해결
    - **API 키 오류**: 환경변수 설정 확인
    - **생성 실패**: 인터넷 연결 및 API 키 한도 확인
    - **저장 실패**: 파일 권한 및 디스크 공간 확인
    """)
    
    # 세션 상태 정보
    st.subheader("🔍 디버그 정보")
    if st.checkbox("세션 상태 표시"):
        st.write("**세션 상태:**")
        st.write(f"- 채팅 히스토리: {len(getattr(st.session_state, 'chat_history', []))}개")
        st.write(f"- 현재 게임 데이터: {'있음' if getattr(st.session_state, 'current_game_data', None) else '없음'}")
        st.write(f"- 커스터마이저: {'초기화됨' if getattr(st.session_state, 'customizer', None) else '없음'}")
        
        if st.button("🔄 세션 초기화 (모든 데이터 삭제)"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("세션이 초기화되었습니다!")
            st.rerun()
