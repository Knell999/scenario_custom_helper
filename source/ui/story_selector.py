"""
스토리 선택기 UI 컴포넌트
"""
import streamlit as st
from source.utils.story_manager import StoryManager


def render_story_selector():
    """메인페이지용 스토리 선택기"""
    st.header("📚 편집할 스토리를 선택하세요")
    
    # 스토리 매니저 초기화
    if 'story_manager' not in st.session_state:
        st.session_state.story_manager = StoryManager()
    
    # 저장된 스토리 목록
    saved_stories = st.session_state.story_manager.get_saved_stories()
    
    if not saved_stories:
        st.warning("📁 저장된 스토리가 없습니다.")
        st.info("""
        💡 **스토리가 없다면:**
        - 다른 프로젝트에서 생성한 스토리 파일을 `saved_stories` 폴더에 복사하세요
        - 또는 백업된 스토리 파일이 있는지 확인해보세요
        """)
        return
    
    # 스토리 선택 인터페이스
    col1, col2 = st.columns([3, 1])
    
    with col1:
        story_names = [f"{story['metadata']['story_name']} ({story['metadata']['scenario_type']})" 
                      for story in saved_stories]
        
        selected_story_index = st.selectbox(
            "스토리 목록:",
            range(len(story_names)),
            format_func=lambda x: story_names[x] if x < len(story_names) else "선택하세요",
            key="main_story_selector"
        )
    
    with col2:
        st.write("") # 간격 조정
        st.write("") # 간격 조정
        load_button = st.button("📖 불러오기", type="primary", use_container_width=True)
    
    # 선택된 스토리 정보 표시
    if selected_story_index < len(saved_stories):
        selected_story_info = saved_stories[selected_story_index]
        
        # 스토리 미리보기
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.info(f"**📝 제목**  \n{selected_story_info['metadata']['story_name']}")
            
        with col_info2:
            st.info(f"**🎭 유형**  \n{selected_story_info['metadata']['scenario_type']}")
            
        with col_info3:
            file_size = selected_story_info.get('size', 0)
            size_kb = file_size / 1024 if file_size > 0 else 0
            st.info(f"**📊 크기**  \n{size_kb:.1f} KB")
        
        # 불러오기 버튼 처리
        if load_button:
            # Load the full story from file
            loaded_story = st.session_state.story_manager.load_story(selected_story_info['filepath'])
            
            if loaded_story:
                # Handle both old format (direct array) and new format (with metadata)
                if isinstance(loaded_story, list):
                    # Old format: direct array of game data
                    st.session_state.current_game_data = loaded_story
                    story_name = selected_story_info['filename'].replace('.json', '')
                else:
                    # New format: with metadata wrapper
                    st.session_state.current_game_data = loaded_story['story_data']
                    story_name = loaded_story['metadata'].get('story_name', selected_story_info['filename'].replace('.json', ''))
                
                st.success(f"✅ '{story_name}' 스토리를 불러왔습니다!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ 스토리 불러오기에 실패했습니다.")
    
    # 스토리 관리 옵션
    with st.expander("🛠️ 스토리 관리"):
        st.subheader("스토리 삭제")
        
        col_del1, col_del2 = st.columns([2, 1])
        
        with col_del1:
            delete_story_index = st.selectbox(
                "삭제할 스토리:",
                range(len(story_names)),
                format_func=lambda x: story_names[x] if x < len(story_names) else "선택하세요",
                key="delete_story_selector"
            )
        
        with col_del2:
            st.write("") # 간격 조정
            if st.button("🗑️ 삭제", type="secondary", use_container_width=True):
                if delete_story_index < len(saved_stories):
                    story_filepath = saved_stories[delete_story_index]['filepath']
                    story_name = saved_stories[delete_story_index]['metadata']['story_name']
                    
                    if st.session_state.story_manager.delete_story(story_filepath):
                        st.success(f"✅ '{story_name}' 스토리가 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 스토리 삭제에 실패했습니다.")
