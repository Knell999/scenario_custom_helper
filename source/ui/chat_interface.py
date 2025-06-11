"""
채팅 인터페이스 UI 컴포넌트 - 스토리 편집 전용
"""
import streamlit as st
import json


def render_chat_interface(customizer):
    """채팅 인터페이스 렌더링 - 스토리 편집 전용"""
    
    # 스토리가 선택되었는지 확인
    if not st.session_state.get('current_game_data'):
        st.warning("👈 먼저 스토리를 선택해서 불러와주세요!")
        st.info("""
        **스토리를 불러오는 방법:**
        1. 위의 스토리 목록에서 편집할 스토리를 선택하세요
        2. '📖 불러오기' 버튼을 클릭하세요
        3. 스토리가 로드되면 여기서 편집 요청을 입력할 수 있습니다
        """)
        return
    
    # 스토리 편집 가이드 메시지
    st.info("""
    **✏️ 스토리 편집 모드 - 이런 요청을 해보세요!**
    
    **🎯 스토리 내용 수정:**
    • "주인공 이름을 민수로 바꿔줘"
    • "3턴 이벤트를 더 재미있게 만들어줘"  
    • "마법 왕국 배경을 더 신비롭게 수정해줘"
    • "캐릭터 대사를 더 친근하게 만들어줘"
    
    **📚 교육적 개선:**
    • "투자 설명을 더 쉬운 단어로 바꿔줘"
    • "위험 수준 설명을 더 명확하게 해줘"
    • "분산투자 개념을 강조해줘"
    
    **🚫 처리할 수 없는 요청:**
    • 새로운 게임 생성 (편집만 가능)
    • 실제 투자 조언 
    • 프로그래밍 관련 질문
    • 일반적인 대화
    """)
    
    💾 **수정 완료 후 저장하기:**
    원하는 제목으로 나만의 스토리를 저장할 수 있어요!
    """)
    
    # 채팅 히스토리 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
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
            
            # 사용자 질문 검증
            from source.utils.chatbot_helper import ChatbotHelper
            chatbot_helper = ChatbotHelper()
            validation_result = chatbot_helper.validate_user_request(user_input)
            
            # AI 응답 생성
            with st.chat_message("assistant"):
                if not validation_result["is_valid"]:
                    # 부적절한 질문에 대한 가이드 응답
                    st.error("❌ 요청을 처리할 수 없습니다")
                    st.write(validation_result["guide_message"])
                    
                    if validation_result["suggested_actions"]:
                        st.write("**💡 이런 요청을 해보세요:**")
                        for suggestion in validation_result["suggested_actions"]:
                            st.write(f"• {suggestion}")
                    
                    # 잘못된 요청도 히스토리에 기록
                    guide_response = f"{validation_result['guide_message']}\n\n" + \
                                   "💡 다음과 같은 요청을 해보세요:\n" + \
                                   "\n".join([f"• {s}" for s in validation_result["suggested_actions"]])
                    st.session_state.chat_history.append(("assistant", guide_response))
                    return
                
                with st.spinner("스토리를 수정하고 있습니다..."):
                    try:
                        # 현재 스토리 이름 확인
                        current_story_name = st.session_state.get('current_story_name')
                        
                        # current_story_name이 없으면 current_game_data에서 추출 시도
                        if not current_story_name and st.session_state.get('current_game_data'):
                            # 사용 가능한 스토리 목록에서 매칭 시도
                            customizer_stories = customizer.get_available_stories()
                            if customizer_stories:
                                # 첫 번째 스토리를 기본값으로 사용 (임시 해결책)
                                current_story_name = customizer_stories[0]
                                st.session_state.current_story_name = current_story_name
                        
                        if not current_story_name:
                            error_msg = "스토리 이름을 찾을 수 없습니다. 스토리를 다시 불러와주세요."
                            st.error(error_msg)
                            st.session_state.chat_history.append(("assistant", error_msg))
                            
                            # 디버깅 정보 표시
                            debug_info = customizer.debug_story_info("")
                            with st.expander("🔧 디버깅 정보"):
                                st.json(debug_info)
                            return
                        
                        # 스토리 수정 요청
                        game_data, analysis = customizer.modify_existing_story(
                            current_story_name, user_input, st.session_state.chat_history
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
                            if analysis.get("validation"):
                                validation = analysis["validation"]
                                if validation["is_valid"]:
                                    st.success("✅ 고품질 스토리가 생성되었습니다!")
                                else:
                                    st.warning("⚠️ 일부 품질 이슈가 있습니다:")
                                    for issue in validation["issues"]:
                                        st.write(f"• {issue}")
                            
                            # 개선 제안 표시
                            if analysis.get("suggestions"):
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
                                
                            # 저장 기능 추가
                            st.markdown("---")
                            st.markdown("**💾 수정된 스토리 저장**")
                            
                            # 수정된 스토리 표시용 컨테이너
                            with st.expander("📖 수정된 스토리 미리보기", expanded=False):
                                try:
                                    parsed_data = json.loads(game_data)
                                    if isinstance(parsed_data, list) and len(parsed_data) > 0:
                                        for i, turn in enumerate(parsed_data[:3], 1):  # 처음 3턴만 미리보기
                                            st.markdown(f"**턴 {turn.get('turn_number', i)}**")
                                            st.write(f"📰 {turn.get('news', '뉴스 없음')}")
                                        if len(parsed_data) > 3:
                                            st.write(f"... 및 {len(parsed_data) - 3}개 턴 더")
                                except:
                                    st.write("스토리 데이터를 미리보기할 수 없습니다.")
                            
                            # 저장 UI
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                save_title = st.text_input(
                                    "저장할 스토리 제목을 입력하세요",
                                    placeholder="예: 수정된 마법 왕국 스토리",
                                    key=f"save_title_{len(st.session_state.chat_history)}"
                                )
                            with col2:
                                save_button = st.button(
                                    "💾 저장하기",
                                    type="primary",
                                    key=f"save_button_{len(st.session_state.chat_history)}"
                                )
                            
                            if save_button and save_title.strip():
                                try:
                                    # StoryManager import 추가
                                    from source.utils.story_manager import StoryManager
                                    story_manager = StoryManager()
                                    
                                    # 현재 스토리 정보 가져오기
                                    current_story_name = st.session_state.get('current_story_name', 'unknown')
                                    scenario_type = current_story_name.replace('game_scenario_', '').split('_')[0] if 'game_scenario_' in current_story_name else 'custom'
                                    
                                    # 사용자 요청 히스토리 수집
                                    user_requests = [msg for role, msg in st.session_state.chat_history if role == "user"]
                                    
                                    # 스토리 저장
                                    saved_path = story_manager.save_story(
                                        story_data=game_data,
                                        story_name=save_title.strip(),
                                        scenario_type=scenario_type,
                                        user_requests=user_requests
                                    )
                                    
                                    st.success(f"✅ 스토리가 성공적으로 저장되었습니다!")
                                    st.info(f"📁 저장 위치: `{saved_path}`")
                                    
                                    # 저장 후 알림 메시지를 채팅에 추가
                                    save_msg = f"📝 스토리 '{save_title.strip()}'가 저장되었습니다."
                                    st.session_state.chat_history.append(("assistant", save_msg))
                                    
                                except Exception as save_error:
                                    st.error(f"저장 중 오류가 발생했습니다: {str(save_error)}")
                            elif save_button and not save_title.strip():
                                st.warning("저장할 스토리 제목을 입력해주세요.")
                                
                        elif analysis and analysis.get("error"):
                            # 에러 메시지가 있는 경우
                            error_msg = analysis["error"]
                            st.error(error_msg)
                            st.session_state.chat_history.append(("assistant", error_msg))
                            
                            # 디버깅 정보 표시
                            debug_info = customizer.debug_story_info(current_story_name)
                            with st.expander("🔧 디버깅 정보"):
                                st.json(debug_info)
                        else:
                            error_msg = "죄송해요, 스토리 수정에 실패했습니다. 다시 시도해주세요."
                            st.error(error_msg)
                            st.session_state.chat_history.append(("assistant", error_msg))
                            
                            # 디버깅 정보 표시
                            debug_info = customizer.debug_story_info(current_story_name)
                            with st.expander("🔧 디버깅 정보"):
                                st.json(debug_info)
                            
                    except Exception as e:
                        error_msg = f"오류가 발생했습니다: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append(("assistant", error_msg))
    
    # 채팅 히스토리 클리어 버튼
    if st.button("💬 대화 초기화", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()