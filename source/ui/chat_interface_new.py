"""
채팅 인터페이스 UI 컴포넌트 - 스토리 편집 기능 포함
"""
import streamlit as st
import json


def render_chat_interface(customizer):
    """채팅 인터페이스 렌더링 - 스토리 편집 전용"""
    
    # 스토리가 선택되었는지 확인
    if not st.session_state.get('current_game_data'):
        st.warning("👈 먼저 사이드바에서 편집할 스토리를 선택해주세요!")
        return
    
    # 스토리 편집 가이드 메시지
    st.info(f"""
    **✏️ 스토리 편집 모드**
    
    💡 **이런 수정을 요청해보세요:**
    • 캐릭터 이름을 바꿔줘
    • 3턴 이벤트를 더 재미있게 만들어줘
    • 배경을 우주로 바꿔줘
    • 대화를 더 재미있게 수정해줘
    • 뉴스 내용을 더 쉽게 바꿔줘
    
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
                        # 스토리 수정 모드 전용
                        game_data, analysis = customizer.modify_existing_story(
                            user_input, st.session_state.chat_history
                        )
                        
                        if game_data and analysis:
                            st.session_state.current_game_data = game_data
                            
                            # 의도 분석 결과 표시
                            intent_type = analysis["intent"]["type"]
                            intent_display = {
                                "character": "🧙‍♀️ 캐릭터 수정",
                                "setting": "🌍 배경 수정", 
                                "events": "📊 이벤트 수정",
                                "dialogue": "📖 대화 수정",
                                "general": "💬 일반 수정"
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
                                    st.metric("수정된 게임 턴", len(parsed_data))
                            except:
                                pass
                                
                        else:
                            error_msg = "죄송해요, 스토리 수정에 실패했습니다. 다시 시도해주세요."
                            st.error(error_msg)
                            st.session_state.chat_history.append(("assistant", error_msg))
                            
                    except Exception as e:
                        error_msg = f"오류가 발생했습니다: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append(("assistant", error_msg))
    
    # 채팅 히스토리 클리어 버튼
    if st.button("💬 대화 초기화", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()
