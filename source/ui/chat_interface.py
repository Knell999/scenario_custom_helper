"""
채팅 인터페이스 UI 컴포넌트
"""
import streamlit as st
import json


def render_chat_interface(customizer, scenario_type):
    """채팅 인터페이스 렌더링"""
    st.header("💬 투자 학습 챗봇")
    
    # 투자 방식별 가이드 메시지
    investment_focus = getattr(st.session_state, 'investment_focus', 'stable_investment')
    
    focus_guides = {
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
    
    current_guide = focus_guides[investment_focus]
    
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
        user_input = st.chat_input("어떤 스토리를 만들고 싶나요?")
        
        if user_input:
            # 사용자 메시지 추가
            st.session_state.chat_history.append(("user", user_input))
            st.chat_message("user").write(user_input)
            
            # AI 응답 생성
            with st.chat_message("assistant"):
                with st.spinner("스토리를 생성하고 있습니다..."):
                    try:
                        # 커스텀 시나리오 생성 (고급 기능 포함)
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
