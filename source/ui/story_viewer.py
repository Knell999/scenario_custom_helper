"""
스토리 뷰어 UI 컴포넌트
"""
import streamlit as st
import json
from datetime import datetime


def render_story_viewer(scenario_type, customizer):
    """스토리 뷰어 렌더링"""
    st.header("📖 생성된 스토리")
    
    if st.session_state.current_game_data:
        try:
            # Handle both JSON string and already-parsed data
            if isinstance(st.session_state.current_game_data, str):
                # JSON 데이터 파싱
                game_data = json.loads(st.session_state.current_game_data)
            else:
                # Already parsed data (from loaded stories)
                game_data = st.session_state.current_game_data
            
            # 탭으로 구분하여 표시
            tab1, tab2 = st.tabs(["📚 스토리 미리보기", "💾 JSON 데이터"])
            
            with tab1:
                if isinstance(game_data, list):
                    # 스토리 평가 기능
                    render_story_rating(scenario_type, customizer)
                    
                    st.markdown("---")
                    
                    # 스토리 정보 표시
                    st.success(f"🎮 총 {len(game_data)}개의 게임 턴이 생성되었습니다!")
                    
                    # 각 턴의 스토리 표시
                    for i, turn_data in enumerate(game_data[:3]):  # 처음 3개만 미리보기
                        with st.expander(f"📅 Day {i+1} 미리보기", expanded=(i==0)):
                            if 'situation' in turn_data:
                                st.write("**상황:**")
                                st.write(turn_data['situation'])
                            
                            if 'shops' in turn_data:
                                st.write("**상점 정보:**")
                                for shop in turn_data['shops']:
                                    st.write(f"• **{shop.get('name', '알 수 없는 상점')}**: {shop.get('description', '설명 없음')}")
                    
                    if len(game_data) > 3:
                        st.info(f"+ {len(game_data) - 3}개 더 많은 턴이 있습니다.")
                
                else:
                    st.write("생성된 게임 데이터:")
                    st.json(game_data)
            
            with tab2:
                st.subheader("📊 게임 데이터 구조")
                
                # Handle both JSON string and already-parsed data for display
                if isinstance(st.session_state.current_game_data, str):
                    display_data = st.session_state.current_game_data
                else:
                    display_data = json.dumps(st.session_state.current_game_data, ensure_ascii=False, indent=2)
                
                st.code(display_data, language="json")
                
                # 저장 및 다운로드 기능
                render_save_download_section(scenario_type)
                
        except json.JSONDecodeError:
            st.error("생성된 데이터가 올바른 JSON 형식이 아닙니다.")
            st.code(st.session_state.current_game_data)
    else:
        render_example_requests()


def render_story_rating(scenario_type, customizer):
    """스토리 평가 섹션 렌더링"""
    col_rating, col_feedback = st.columns([1, 2])
    
    with col_rating:
        st.subheader("⭐ 스토리 평가")
        rating = st.slider("만족도", 1, 5, 3, key="story_rating")
        
        if st.button("📊 평가 제출", type="primary"):
            st.success(f"⭐ {rating}/5점으로 평가되었습니다!")
    
    with col_feedback:
        st.subheader("💬 피드백")
        feedback = st.text_area(
            "개선사항이나 의견을 남겨주세요",
            placeholder="예: 더 재미있는 캐릭터를 추가해주세요",
            key="story_feedback"
        )
        
        if st.button("🔄 피드백 반영하여 개선", type="secondary"):
            if feedback.strip():
                # 피드백을 반영한 개선 요청
                improvement_request = f"사용자 평가: {rating}/5점. 피드백: {feedback}. 이를 반영하여 스토리를 개선해주세요."
                
                # 채팅 히스토리에 추가하고 개선 요청
                st.session_state.chat_history.append(("user", improvement_request))
                
                with st.spinner("피드백을 반영하여 스토리를 개선하고 있습니다..."):
                    try:
                        improved_data, analysis = customizer.generate_custom_scenario(
                            improvement_request, scenario_type, st.session_state.chat_history
                        )
                        
                        if improved_data:
                            st.session_state.current_game_data = improved_data
                            response = "✨ 피드백을 반영하여 스토리를 개선했습니다!"
                            st.session_state.chat_history.append(("assistant", response))
                            st.success(response)
                            st.rerun()
                    except Exception as e:
                        st.error(f"개선 중 오류 발생: {e}")


def render_save_download_section(scenario_type):
    """저장 및 다운로드 섹션 렌더링"""
    col_save, col_download = st.columns(2)
    
    with col_save:
        st.subheader("💾 스토리 저장")
        story_name = st.text_input(
            "스토리 이름",
            value=f"내가 만든 {scenario_type} 스토리",
            key="story_name_input"
        )
        
        if st.button("💾 저장하기", type="primary"):
            if story_name.strip():
                try:
                    filepath = st.session_state.story_manager.save_story(
                        story_data=st.session_state.current_game_data,
                        story_name=story_name,
                        scenario_type=scenario_type
                    )
                    
                    if filepath:
                        st.success(f"✅ '{story_name}' 스토리가 저장되었습니다!")
                        st.info(f"📁 저장 위치: {filepath}")
                    else:
                        st.error("❌ 저장에 실패했습니다.")
                except Exception as e:
                    st.error(f"저장 중 오류 발생: {e}")
            else:
                st.warning("스토리 이름을 입력해주세요.")
    
    with col_download:
        st.subheader("📥 JSON 다운로드")
        
        # Ensure data is in JSON string format for download
        if isinstance(st.session_state.current_game_data, str):
            download_data = st.session_state.current_game_data
        else:
            download_data = json.dumps(st.session_state.current_game_data, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📄 JSON 파일 다운로드",
            data=download_data,
            file_name=f"custom_game_{scenario_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def render_example_requests():
    """예시 요청 섹션 렌더링"""
    st.info("💬 왼쪽 채팅에서 원하는 스토리를 요청해보세요!")
    
    # 카테고리별 예시 요청
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 🧙‍♀️ 캐릭터 변경 예시")
        character_examples = [
            "주인공을 용감한 공주로 바꿔줘",
            "마법사 대신 기사가 나오게 해줘",
            "동물 친구들이 등장하는 스토리로 만들어줘",
            "로봇이 주인공인 이야기로 바꿔줘"
        ]
        for example in character_examples:
            if st.button(f"💭 {example}", key=f"char_{example[:10]}"):
                st.session_state.example_request = example
                st.rerun()
        
        st.markdown("### 🌍 배경 변경 예시")
        setting_examples = [
            "우주를 배경으로 하는 게임으로 만들어줘",
            "바다 속 세계로 배경을 바꿔줘",
            "정글 모험 스토리로 만들어줘",
            "미래 도시가 배경인 이야기로 해줘"
        ]
        for example in setting_examples:
            if st.button(f"🌟 {example}", key=f"setting_{example[:10]}"):
                st.session_state.example_request = example
                st.rerun()
    
    with col_b:
        st.markdown("### 📊 난이도 조절 예시")
        difficulty_examples = [
            "더 쉬운 단어로 설명해줘",
            "좀 더 어려운 내용으로 만들어줘",
            "5세 아이도 이해할 수 있게 해줘",
            "더 자세한 설명을 추가해줘"
        ]
        for example in difficulty_examples:
            if st.button(f"📚 {example}", key=f"diff_{example[:10]}"):
                st.session_state.example_request = example
                st.rerun()
        
        st.markdown("### 📖 스토리 개선 예시")
        story_examples = [
            "더 재미있는 모험 요소를 넣어줘",
            "미스터리한 요소를 추가해줘",
            "친구들과 함께하는 이야기로 만들어줘",
            "더 흥미진진한 스토리로 바꿔줘"
        ]
        for example in story_examples:
            if st.button(f"✨ {example}", key=f"story_{example[:10]}"):
                st.session_state.example_request = example
                st.rerun()


def handle_example_request(customizer, scenario_type):
    """예시 요청 처리"""
    if hasattr(st.session_state, 'example_request'):
        user_input = st.session_state.example_request
        delattr(st.session_state, 'example_request')
        
        # 사용자 메시지 추가
        st.session_state.chat_history.append(("user", user_input))
        
        # AI 응답 생성
        with st.spinner("스토리를 생성하고 있습니다..."):
            try:
                game_data, analysis = customizer.generate_custom_scenario(
                    user_input, scenario_type, st.session_state.chat_history
                )
                
                if game_data and analysis:
                    st.session_state.current_game_data = game_data
                    response = f"✨ '{user_input}'을 반영한 새로운 스토리를 만들었어요!"
                    st.session_state.chat_history.append(("assistant", response))
                    st.success(response)
                    st.rerun()
                else:
                    error_msg = "스토리 생성에 실패했습니다. 다시 시도해주세요."
                    st.session_state.chat_history.append(("assistant", error_msg))
                    st.error(error_msg)
            except Exception as e:
                error_msg = f"오류가 발생했습니다: {str(e)}"
                st.session_state.chat_history.append(("assistant", error_msg))
                st.error(error_msg)
