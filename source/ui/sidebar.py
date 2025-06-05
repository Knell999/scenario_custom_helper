"""
사이드바 UI 컴포넌트
"""
import streamlit as st
from source.utils.config import load_api_key
from source.utils.story_manager import StoryManager


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.header("🎯 스토리 편집 설정")
        
        # 모드 선택 (새 기능)
        mode_selection = st.radio(
            "작업 모드 선택",
            ["📝 스토리 편집", "🆕 새 스토리 생성"],
            key="work_mode_radio"
        )
        
        # 선택된 모드에 따라 work_mode 설정
        if mode_selection == "📝 스토리 편집":
            work_mode = "edit"
            st.info("💡 저장된 스토리를 선택하고 수정할 수 있습니다.")
        else:
            work_mode = "create"
            st.info("💡 새로운 스토리를 처음부터 만들 수 있습니다.")
        
        # 세션 상태에 저장 (key 충돌 방지)
        if 'work_mode' not in st.session_state or st.session_state.work_mode != work_mode:
            st.session_state.work_mode = work_mode
        
        st.markdown("---")
        
        # 기존 시나리오 타입 선택 (새 스토리 생성 시에만)
        scenario_type = "magic_kingdom"  # 기본값 설정
        if st.session_state.get('work_mode', 'create') == 'create':
            scenario_type = st.selectbox(
                "기본 스토리 템플릿",
                ["magic_kingdom", "foodtruck_kingdom", "moonlight_thief"],
                format_func=lambda x: {
                    "magic_kingdom": "🏰 마법 왕국",
                    "foodtruck_kingdom": "🚚 푸드트럭 왕국",
                    "moonlight_thief": "🌙 달빛 도둑"
                }[x]
            )
            
            # 세션 상태에 저장
            st.session_state.selected_scenario = scenario_type
        
        st.markdown("---")
        
        # 투자 방식 학습 포커스 선택 (편집 모드가 아닐 때만)
        if st.session_state.get('work_mode', 'create') == 'create':
            st.subheader("📈 학습 목표 선택")
            investment_focus = st.selectbox(
                "어떤 투자 방식을 학습하고 싶나요?",
                ["stable_investment", "diversification", "trading_timing", "growth_investment"],
                format_func=lambda x: {
                    "stable_investment": "🛡️ 안정형 투자",
                    "diversification": "🥚 분산투자",
                    "trading_timing": "⏰ 매매 타이밍",
                    "growth_investment": "📈 성장형 투자"
                }[x]
            )
            
            # 세션 상태에 저장
            st.session_state.investment_focus = investment_focus
            
            # 투자 방식별 설명 표시
            focus_descriptions = {
                "stable_investment": "💡 안전하고 꾸준한 투자 방법을 배워보세요",
                "diversification": "💡 리스크를 줄이는 분산투자 전략을 익혀보세요",
                "trading_timing": "💡 언제 사고 팔지 판단하는 방법을 학습해보세요",
                "growth_investment": "💡 성장 가능성이 높은 투자 기회를 찾는 법을 배워보세요"
            }
            st.info(focus_descriptions[investment_focus])
        else:
            # 편집 모드일 때는 스토리 편집으로 설정
            st.session_state.investment_focus = "story_editing"
            st.info("💡 기존 스토리를 수정하고 개선할 수 있습니다")
        
        st.markdown("---")
        
        # 스토리 관리
        st.header("📚 저장된 스토리")
        
        # 스토리 매니저 초기화
        if 'story_manager' not in st.session_state:
            st.session_state.story_manager = StoryManager()
        
        # 저장된 스토리 목록
        saved_stories = st.session_state.story_manager.get_saved_stories()
        
        if saved_stories:
            story_names = [f"{story['metadata']['story_name']} ({story['metadata']['scenario_type']})" 
                          for story in saved_stories]
            
            selected_story_index = st.selectbox(
                "저장된 스토리 선택",
                range(len(story_names)),
                format_func=lambda x: story_names[x] if x < len(story_names) else "선택하세요"
            )
            
            col_load, col_delete = st.columns(2)
            
            with col_load:
                if st.button("📖 불러오기", type="primary"):
                    selected_story_info = saved_stories[selected_story_index]
                    # Load the full story from file
                    loaded_story = st.session_state.story_manager.load_story(selected_story_info['filepath'])
                    
                    # Handle both old format (direct array) and new format (with metadata)
                    if isinstance(loaded_story, list):
                        # Old format: direct array of game data
                        st.session_state.current_game_data = loaded_story
                        story_name = selected_story_info['filename'].replace('.json', '')
                    else:
                        # New format: with metadata wrapper
                        st.session_state.current_game_data = loaded_story['story_data']
                        story_name = loaded_story['metadata'].get('story_name', selected_story_info['filename'].replace('.json', ''))
                    
                    st.success(f"'{story_name}' 스토리를 불러왔습니다!")
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️ 삭제", type="secondary"):
                    story_filepath = saved_stories[selected_story_index]['filepath']
                    if st.session_state.story_manager.delete_story(story_filepath):
                        st.success("삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("삭제 실패")
        else:
            st.info("저장된 스토리가 없습니다.")
        
        st.markdown("---")
        
        # API 키 확인
        api_key = load_api_key()
        if api_key:
            st.success("✅ API 키 로드됨")
        else:
            st.error("❌ API 키를 찾을 수 없습니다")
            st.info("`.env` 파일에 `OPENAI_API_KEY`를 설정해주세요")
    
    return scenario_type
