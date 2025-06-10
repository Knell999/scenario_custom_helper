"""
스토리 뷰어 UI 컴포넌트 - 기존 스토리 편집 기능 포함
"""
import streamlit as st
import json
from datetime import datetime


def render_story_viewer(customizer):
    """스토리 뷰어 렌더링 - 편집 전용"""
    # 선택된 스토리가 있는 경우 해당 스토리 표시
    if hasattr(st.session_state, 'selected_story') and st.session_state.selected_story:
        render_selected_story_viewer(customizer)
    elif st.session_state.get('current_game_data'):
        render_edited_story_viewer(customizer)
    else:
        render_empty_state()


def render_selected_story_viewer(customizer):
    """선택된 기존 스토리 표시"""
    story_name = st.session_state.selected_story
    story_data = customizer.story_editor.load_story(story_name)
    
    if not story_data:
        st.error("선택된 스토리를 불러올 수 없습니다.")
        return
    
    st.info(f"📚 현재 편집 중인 스토리: **{story_name}**")
    
    # 스토리 요약 정보
    summary = customizer.get_story_summary(story_name)
    if summary:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 턴 수", summary.get('total_turns', 0))
        with col2:
            st.metric("캐릭터 수", len(summary.get('characters', [])))
        with col3:
            st.write(f"**최종 수정**")
            st.write(f"{summary.get('last_modified', 'Unknown')}")
    
    # 탭으로 구분하여 표시
    tab1, tab2, tab3 = st.tabs(["📚 스토리 미리보기", "📊 스토리 구조", "💾 JSON 데이터"])
    
    with tab1:
        render_story_preview(story_data)
        
    with tab2:
        render_story_structure(story_data)
        
    with tab3:
        render_json_data(story_data)


def render_edited_story_viewer(customizer):
    """수정된 스토리 표시"""
    st.write("수정된 스토리:")
    
    try:
        if isinstance(st.session_state.current_game_data, str):
            game_data = json.loads(st.session_state.current_game_data)
        else:
            game_data = st.session_state.current_game_data
        
        if isinstance(game_data, list):
            st.success(f"✏️ 총 {len(game_data)}개의 게임 턴이 수정되었습니다!")
            
            # 모든 턴 표시
            for i, turn_data in enumerate(game_data):
                with st.expander(f"📅 Day {i+1} 미리보기", expanded=(i==0)):
                    if 'result' in turn_data:
                        st.write("**상황:**")
                        st.write(turn_data['result'])
                    
                    if 'news' in turn_data:
                        st.write("**뉴스:**")
                        st.write(turn_data['news'])
        else:
            st.json(game_data)
            
    except json.JSONDecodeError:
        st.error("수정된 데이터가 올바른 JSON 형식이 아닙니다.")
        st.code(st.session_state.current_game_data)


def render_empty_state():
    """빈 상태 표시"""
    st.info("💬 왼쪽에서 편집할 스토리를 선택해보세요!")
    
    # 사용 가능한 기능 안내
    st.markdown("""
    ### 🎯 스토리 편집 기능
    
    **📚 스토리 선택**
    - 사이드바에서 저장된 스토리를 선택하세요
    
    **✏️ 편집 요청 예시:**
    - "빵집 주인의 이름을 '토토'로 바꿔줘"
    - "3턴의 이벤트를 더 흥미진진하게 만들어줘"
    - "전체적인 대화를 더 재미있게 수정해줘"
    - "뉴스 내용을 더 쉽게 설명해줘"
    
    **🔍 미리보기 기능:**
    - 선택한 스토리의 구조와 내용을 확인할 수 있어요
    - 수정된 내용을 실시간으로 미리볼 수 있어요
    """)
    
    # 도움말 정보
    with st.expander("💡 사용 팁"):
        st.markdown("""
        - 구체적인 수정 요청을 하면 더 정확한 결과를 얻을 수 있어요
        - 여러 번에 나누어 조금씩 수정하는 것이 좋아요
        - 수정 후에는 백업이 자동으로 생성됩니다
        """)
    
    # 스토리 목록 표시 (있는 경우)
    if 'customizer' in st.session_state:
        available_stories = st.session_state.customizer.get_available_stories()
        if available_stories:
            st.write("**📖 편집 가능한 스토리:**")
            for story in available_stories:
                st.write(f"• {story}")
        else:
            st.warning("저장된 스토리가 없습니다. 스토리 파일을 saved_stories 폴더에 추가해주세요.")


def render_story_preview(story_data):
    """스토리 내용 미리보기 - 전체 턴 표시"""
    if not isinstance(story_data, list):
        st.write("스토리 데이터 형식이 올바르지 않습니다.")
        return
    
    st.success(f"🎮 총 {len(story_data)}개의 게임 턴이 있습니다!")
    
    # 모든 턴 표시
    for i, turn_data in enumerate(story_data):
        with st.expander(f"📅 Day {i+1} 미리보기", expanded=(i==0)):
            if 'result' in turn_data:
                st.write("**📰 상황:**")
                st.write(turn_data['result'])
            
            if 'news' in turn_data:
                st.write("**📢 뉴스:**")
                st.write(turn_data['news'])
            
            if 'stocks' in turn_data:
                st.write("**🏪 상점 정보:**")
                for stock in turn_data['stocks']:
                    st.write(f"• **{stock.get('name', '알 수 없는 상점')}**: {stock.get('current_value', 0)}원 ({stock.get('risk_level', '위험도 미정')})")


def render_story_structure(story_data):
    """스토리 구조 분석 표시"""
    if not isinstance(story_data, list):
        st.write("스토리 데이터 형식이 올바르지 않습니다.")
        return
    
    # 기본 통계
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 턴 수", len(story_data))
    
    with col2:
        # 등장하는 상점/캐릭터 수
        all_shops = set()
        for turn in story_data:
            if 'stocks' in turn:
                for stock in turn['stocks']:
                    all_shops.add(stock.get('name', ''))
        st.metric("등장 상점 수", len(all_shops))
    
    with col3:
        # 평균 상점 가치
        total_values = []
        for turn in story_data:
            if 'stocks' in turn:
                for stock in turn['stocks']:
                    value = stock.get('current_value', 0)
                    if isinstance(value, (int, float)):
                        total_values.append(value)
        avg_value = sum(total_values) / len(total_values) if total_values else 0
        st.metric("평균 상점 가치", f"{avg_value:.1f}")


def render_json_data(story_data):
    """JSON 데이터 표시"""
    st.subheader("📊 스토리 JSON 데이터")
    
    # JSON 형태로 표시
    st.json(story_data)
    
    # 다운로드 버튼
    json_str = json.dumps(story_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📄 JSON 파일 다운로드",
        data=json_str,
        file_name=f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
