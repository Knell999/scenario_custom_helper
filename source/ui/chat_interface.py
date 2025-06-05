"""
채팅 인터페이스 UI 컴포넌트 - 스토리 편집 기능 포함
"""
import streamlit as st
import json


def render_story_selector(customizer):
    """저장된 스토리 선택 인터페이스"""
    st.subheader("📚 편집할 스토리 선택")
    
    # 사용 가능한 스토리 목록 가져오기
    available_stories = customizer.get_available_stories()
    
    if not available_stories:
        st.warning("저장된 스토리가 없습니다. 먼저 스토리를 생성해주세요.")
        return
    
    # 스토리 선택 드롭다운
    selected_story = st.selectbox(
        "편집할 스토리를 선택하세요:",
        options=["선택하지 않음"] + available_stories,
        key="story_selector"
    )
    
    # 세션 상태에 선택된 스토리 저장
    if selected_story != "선택하지 않음":
        st.session_state.selected_story = selected_story
        
        # 스토리 요약 정보 표시
        summary = customizer.get_story_summary(selected_story)
        if summary:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 턴 수", summary.get('total_turns', 0))
            with col2:
                st.metric("캐릭터 수", len(summary.get('characters', [])))
            with col3:
                st.write(f"**최종 수정:** {summary.get('last_modified', 'Unknown')}")
        
        st.success(f"✅ '{selected_story}' 스토리가 선택되었습니다. 이제 수정 요청을 입력하세요!")
        
        # 수정 예시 제공
        with st.expander("💡 수정 요청 예시"):
            st.write("""
            **캐릭터 수정:**
            - "빵집 주인의 이름을 '토토'로 바꿔줘"
            - "마법사 캐릭터를 더 친근하게 만들어줘"
            
            **스토리 내용 수정:**
            - "3턴에서 일어나는 사건을 더 흥미진진하게 바꿔줘"
            - "뉴스 내용을 더 아이들이 이해하기 쉽게 수정해줘"
            
            **배경 수정:**
            - "마법 왕국을 우주 배경으로 바꿔줘"
            - "계절을 겨울로 설정해줘"
            
            **대화 수정:**
            - "캐릭터들의 말을 더 재미있게 바꿔줘"
            - "설명을 더 간단하게 만들어줘"
            """)
    else:
        if 'selected_story' in st.session_state:
            del st.session_state.selected_story


def render_story_editing_guide():
    """스토리 편집 가이드"""
    st.subheader("📝 스토리 편집 가이드")
    
    guide_tabs = st.tabs(["🎯 편집 유형", "💡 편집 팁", "⚠️ 주의사항"])
    
    with guide_tabs[0]:
        st.write("""
        **📚 스토리 편집 유형**
        
        🧙‍♀️ **캐릭터 편집**: 등장인물의 이름, 성격, 외모 수정
        🌍 **배경 편집**: 시간, 장소, 환경 설정 변경  
        📰 **이벤트 편집**: 게임 내 사건, 뉴스, 상황 수정
        💬 **대화 편집**: 캐릭터 대사와 설명 텍스트 수정
        📊 **데이터 편집**: 주식 가격, 위험도 등 게임 데이터 조정
        """)
        
    with guide_tabs[1]:
        st.write("""
        **💡 효과적인 편집 팁**
        
        ✅ **구체적으로 요청하세요**: "3턴의 빵집 이벤트를 수정해줘"
        ✅ **목적을 명시하세요**: "더 재미있게", "이해하기 쉽게" 
        ✅ **단계별로 수정하세요**: 한 번에 하나씩 수정
        ✅ **확인 후 다음 단계**: 수정 결과 확인 후 추가 요청
        """)
        
    with guide_tabs[2]:
        st.write("""
        **⚠️ 편집 시 주의사항**
        
        🔒 원본 파일은 자동으로 백업됩니다
        🎯 교육 목적에 맞는 내용으로 유지됩니다  
        👶 10세 이하 아동 대상 언어로 작성됩니다
        📊 게임 구조와 균형은 자동으로 검증됩니다
        """)


def render_chat_interface(customizer, scenario_type):
    """채팅 인터페이스 렌더링"""
    st.header("💬 스토리 편집 챗봇")
    
    # 스토리 선택 섹션
    render_story_selector(customizer)
    
    # 투자 방식별 가이드 메시지
    investment_focus = getattr(st.session_state, 'investment_focus', 'stable_investment')
    
    focus_guides = {
        "story_editing": {
            "emoji": "✏️",
            "title": "스토리 편집 모드",
            "examples": [
                "캐릭터 이름을 바꿔줘",
                "3턴 이벤트를 더 재미있게 만들어줘",
                "배경을 우주로 바꿔줘"
            ]
        },
        "stable_investment": {
            "emoji": "🛡️",
            "title": "안정형 투자 학습",
            "examples": [
                "안정적인 투자 방법을 알려줘",
                "리스크를 줄이는 방법을 배우고 싶어",
                "예금과 적금의 차이를 설명해줘"
            ]
        },
        "diversification": {
            "emoji": "🥚",
            "title": "분산투자 학습",
            "examples": [
                "분산투자가 왜 중요한지 알려줘",
                "포트폴리오를 어떻게 구성하나요?",
                "계란을 한 바구니에 담지 말라는 뜻을 설명해줘"
            ]
        },
        "trading_timing": {
            "emoji": "⏰",
            "title": "매매 타이밍 학습",
            "examples": [
                "언제 사고 팔지 어떻게 정하나요?",
                "매수 매도 타이밍을 알려줘",
                "감정적 투자를 피하는 방법을 배우고 싶어"
            ]
        },
        "growth_investment": {
            "emoji": "📈",
            "title": "성장형 투자 학습",
            "examples": [
                "성장 가능성이 높은 투자를 알려줘",
                "높은 수익과 높은 위험의 관계를 설명해줘",
                "장기 투자의 장점을 배우고 싶어"
            ]
        }
    }
    
    # 현재 투자 포커스에 따른 가이드 표시
    current_guide = focus_guides.get(investment_focus, focus_guides["stable_investment"])
    
    # 선택된 스토리가 있으면 편집 모드 가이드 표시
    if hasattr(st.session_state, 'selected_story') and st.session_state.selected_story:
        current_guide = focus_guides["story_editing"]
    
    # 가이드 메시지 표시
    st.info(f"""
    **{current_guide['emoji']} {current_guide['title']}**
    
    💡 **이런 질문을 해보세요:**
    • {current_guide['examples'][0]}
    • {current_guide['examples'][1]}
    • {current_guide['examples'][2]}
    
    난이도 조절도 가능해요: "더 쉽게 설명해줘", "더 자세히 알려줘"
    """)
    
    # 채팅 히스토리 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 현재 게임 데이터 초기화
    if 'current_game_data' not in st.session_state:
        st.session_state.current_game_data = None
    
    # 채팅 인터페이스
    with st.container():
        # 채팅 히스토리 표시
        for i, (role, message) in enumerate(st.session_state.chat_history):
            if role == "user":
                st.chat_message("user").write(message)
            else:
                st.chat_message("assistant").write(message)
        
        # 사용자 입력
        user_input = st.chat_input("스토리를 어떻게 수정하고 싶나요?")
        
        if user_input:
            # 사용자 메시지 추가
            st.session_state.chat_history.append(("user", user_input))
            st.chat_message("user").write(user_input)
            
            # AI 응답 생성
            with st.chat_message("assistant"):
                with st.spinner("스토리를 수정하고 있습니다..."):
                    try:
                        # 선택된 스토리가 있으면 수정 모드, 없으면 생성 모드
                        if hasattr(st.session_state, 'selected_story') and st.session_state.selected_story:
                            # 스토리 수정 모드
                            game_data, analysis = customizer.modify_existing_story(
                                st.session_state.selected_story, user_input, st.session_state.chat_history
                            )
                        else:
                            # 새 스토리 생성 모드 (기존 기능 유지)
                            game_data, analysis = customizer.generate_custom_scenario(
                                user_input, scenario_type, st.session_state.chat_history
                            )
                        
                        if game_data and analysis:
                            st.session_state.current_game_data = game_data
                            
                            # 의도 분석 결과 표시
                            intent_type = analysis["intent"]["type"]
                            intent_display = {
                                "character_change": "🧙‍♀️ 캐릭터 변경",
                                "setting_change": "🌍 배경 변경", 
                                "difficulty_adjustment": "📊 난이도 조절",
                                "story_enhancement": "📖 스토리 개선",
                                "general": "💬 일반 요청"
                            }
                            
                            response = f"✨ 요청을 분석했습니다: {intent_display.get(intent_type, intent_type)}"
                            st.write(response)
                            
                            # 품질 검증 결과 표시
                            if analysis["validation"]:
                                validation = analysis["validation"]
                                if validation["is_valid"]:
                                    st.success("✅ 고품질 스토리가 생성되었습니다!")
                                else:
                                    st.warning("⚠️ 일부 품질 이슈가 있습니다:")
                                    for issue in validation["issues"]:
                                        st.write(f"• {issue}")
                            
                            # 개선 제안 표시
                            if analysis["suggestions"]:
                                st.write("**💡 추가 개선 제안:**")
                                for suggestion in analysis["suggestions"]:
                                    st.write(f"• {suggestion}")
                            
                            st.session_state.chat_history.append(("assistant", response))
                            
                            # 게임 데이터 파싱하여 간단한 요약 표시
                            try:
                                parsed_data = json.loads(game_data)
                                if isinstance(parsed_data, list) and len(parsed_data) > 0:
                                    st.metric("생성된 게임 턴", len(parsed_data))
                            except:
                                pass
                                
                        else:
                            error_msg = "죄송해요, 스토리 생성에 실패했습니다. 다시 시도해주세요."
                            st.error(error_msg)
                            st.session_state.chat_history.append(("assistant", error_msg))
                            
                    except Exception as e:
                        error_msg = f"오류가 발생했습니다: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append(("assistant", error_msg))
    
    # 채팅 히스토리 클리어 버튼
    if st.button("💬 대화 초기화", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.current_game_data = None
        st.rerun()
