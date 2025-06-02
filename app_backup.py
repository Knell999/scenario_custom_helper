"""
스토리 게임 커스터마이저 - 메인 애플리케이션
"""
import streamlit as st
import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 모듈 import
from source.components.game_customizer import GameCustomizer
from source.ui.sidebar import render_sidebar
from source.ui.chat_interface import render_chat_interface
from source.ui.story_viewer import render_story_viewer
from source.ui.info_tabs import render_info_tabs
from source.utils.config import load_api_key

class GameCustomizer:
    def __init__(self):
        """게임 커스터마이저 초기화"""
        self.llm = None
        self.chatbot_helper = ChatbotHelper()
        self.initialize_llm_model()
        
    def initialize_llm_model(self):
        """LLM 모델 초기화"""
        try:
            self.llm = initialize_llm()
            return True
        except Exception as e:
            st.error(f"LLM 모델 초기화 실패: {e}")
            return False
    
    def generate_custom_scenario(self, user_input, scenario_type="magic_kingdom", chat_history=None):
        """사용자 입력을 바탕으로 커스텀 시나리오 생성"""
        if not self.llm:
            return None, None
            
        # 사용자 의도 분석
        intent = self.chatbot_helper.analyze_user_intent(user_input)
        
        # 대화 컨텍스트 포함
        conversation_summary = self.chatbot_helper.create_conversation_summary(chat_history or [])
        
        # 커스터마이징을 위한 프롬프트 생성
        custom_prompt = self.create_advanced_customization_prompt(
            user_input, scenario_type, intent, conversation_summary
        )
        
        # 프롬프트 템플릿 생성
        prompt_template = create_prompt_template(get_system_prompt())
        
        # 게임 데이터 생성
        game_data = generate_game_data(self.llm, prompt_template, custom_prompt)
        
        # 생성된 콘텐츠 검증
        validation_result = None
        if game_data:
            validation_result = self.chatbot_helper.validate_generated_content(game_data)
        
        return game_data, {
            "intent": intent,
            "validation": validation_result,
            "suggestions": self.chatbot_helper.suggest_improvements(user_input, scenario_type)
        }
    
    def create_advanced_customization_prompt(self, user_input, scenario_type, intent, conversation_summary):
        """고급 커스터마이징 프롬프트 생성"""
        base_prompt = get_game_scenario_prompt(scenario_type)
        
        customization_instruction = f"""
        기본 시나리오: {scenario_type}
        
        대화 컨텍스트: {conversation_summary}
        
        사용자의 현재 요청: {user_input}
        감지된 의도: {intent['type']}
        관련 키워드: {', '.join(intent['keywords'])}
        사용자 감정: {intent['sentiment']}
        
        {self.chatbot_helper.generate_response_prompt(user_input, intent, scenario_type)}
        
        중요 지침:
        1. 10세 이하 아동이 이해하기 쉬운 언어 사용
        2. 투자와 돈 관리의 기본 개념을 자연스럽게 학습할 수 있도록 구성
        3. 재미있고 흥미로운 스토리텔링 요소 포함
        4. 안전하고 교육적인 내용으로 구성
        5. JSON 형식으로 정확히 출력
        
        기본 시나리오 참고:
        {base_prompt}
        """
        
        return customization_instruction

def main():
    st.set_page_config(
        page_title="스토리 게임 커스터마이저",
        page_icon="🎮",
        layout="wide"
    )
    
    # 제목
    st.title("🎮 스토리 게임 커스터마이저")
    st.markdown("---")
    
    # 사이드바: 게임 설정
    with st.sidebar:
        st.header("🎯 게임 설정")
        
        # 시나리오 타입 선택
        scenario_type = st.selectbox(
            "시나리오 선택",
            ["magic_kingdom", "foodtruck_kingdom", "moonlight_thief"],
            format_func=lambda x: {
                "magic_kingdom": "🏰 마법 왕국",
                "foodtruck_kingdom": "🚚 푸드트럭 왕국",
                "moonlight_thief": "🌙 달빛 도둑"
            }[x]
        )
        
        st.markdown("---")
        
        # 스토리 관리 초기화
        if 'story_manager' not in st.session_state:
            st.session_state.story_manager = StoryManager()
        
        # 저장된 스토리 관리
        st.header("💾 저장된 스토리")
        saved_stories = st.session_state.story_manager.get_saved_stories()
        
        if saved_stories:
            st.subheader("📚 불러오기")
            for story in saved_stories[:5]:  # 최근 5개만 표시
                metadata = story["metadata"]
                story_name = metadata.get("story_name", "이름 없음")
                created_at = metadata.get("created_at", "")
                if created_at:
                    created_at = created_at[:19].replace("T", " ")
                
                with st.expander(f"📖 {story_name}", expanded=False):
                    st.write(f"**생성일**: {created_at}")
                    st.write(f"**시나리오**: {metadata.get('scenario_type', '알 수 없음')}")
                    st.write(f"**크기**: {story['size']} bytes")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📂 불러오기", key=f"load_{story['filename']}"):
                            try:
                                loaded_story = st.session_state.story_manager.load_story(story["filepath"])
                                st.session_state.current_game_data = json.dumps(
                                    loaded_story["story_data"], ensure_ascii=False, indent=2
                                )
                                st.success(f"'{story_name}' 스토리를 불러왔습니다!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"불러오기 실패: {e}")
                    
                    with col2:
                        if st.button("🗑️ 삭제", key=f"delete_{story['filename']}"):
                            if st.session_state.story_manager.delete_story(story["filepath"]):
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
    
    # 메인 컨테이너
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("💬 챗봇과 대화하기")
        
        # 게임 커스터마이저 초기화
        if 'customizer' not in st.session_state:
            st.session_state.customizer = GameCustomizer()
        
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
                            game_data, analysis = st.session_state.customizer.generate_custom_scenario(
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
                                
                                st.info(f"**감지된 요청**: {intent_display.get(intent_type, '일반 요청')}")
                                
                                # 성공 메시지
                                response = f"✨ 멋진 아이디어네요! '{user_input}'을 반영한 새로운 스토리를 만들었어요!"
                                st.write(response)
                                
                                # 검증 결과 표시
                                if analysis["validation"]:
                                    validation = analysis["validation"]
                                    if validation["is_valid"]:
                                        st.success("✅ 고품질 스토리가 생성되었습니다!")
                                    else:
                                        st.warning("⚠️ 스토리가 생성되었지만 일부 개선이 필요할 수 있습니다.")
                                        if validation["issues"]:
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
    
    with col2:
        st.header("📖 생성된 스토리")
        
        if st.session_state.current_game_data:
            try:
                # JSON 데이터 파싱
                game_data = json.loads(st.session_state.current_game_data)
                
                # 탭으로 구분하여 표시
                tab1, tab2 = st.tabs(["📚 스토리 미리보기", "💾 JSON 데이터"])
                
                with tab1:
                    if isinstance(game_data, list):
                        # 스토리 평가 기능
                        col_rating, col_feedback = st.columns([1, 2])
                        
                        with col_rating:
                            st.subheader("⭐ 스토리 평가")
                            rating = st.slider("이 스토리는 어떤가요?", 1, 5, 3, key="story_rating")
                            
                            if rating >= 4:
                                st.success("😊 훌륭해요!")
                            elif rating >= 3:
                                st.info("👍 괜찮아요!")
                            else:
                                st.warning("🤔 더 개선이 필요해요")
                        
                        with col_feedback:
                            st.subheader("💬 피드백")
                            feedback = st.text_area(
                                "이 스토리에 대한 의견을 남겨주세요",
                                placeholder="더 재미있게 만들고 싶은 부분이나 좋았던 점을 알려주세요!",
                                height=100
                            )
                            
                            if st.button("📝 피드백 반영하여 개선", type="primary"):
                                if feedback:
                                    # 피드백을 반영한 개선 요청
                                    improvement_request = f"사용자 평가: {rating}/5점. 피드백: {feedback}. 이를 반영하여 스토리를 개선해주세요."
                                    
                                    # 채팅 히스토리에 추가하고 개선 요청
                                    st.session_state.chat_history.append(("user", improvement_request))
                                    
                                    with st.spinner("피드백을 반영하여 스토리를 개선하고 있습니다..."):
                                        try:
                                            improved_data, analysis = st.session_state.customizer.generate_custom_scenario(
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
                    st.code(st.session_state.current_game_data, language="json")
                    
                    # 저장 및 다운로드 기능
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
                                    # 사용자 요청 히스토리 추출
                                    user_requests = [msg for role, msg in st.session_state.chat_history if role == "user"]
                                    
                                    # 스토리 저장
                                    filepath = st.session_state.story_manager.save_story(
                                        st.session_state.current_game_data,
                                        story_name.strip(),
                                        scenario_type,
                                        user_requests
                                    )
                                    
                                    st.success(f"✅ '{story_name}' 스토리가 저장되었습니다!")
                                    st.info(f"📁 저장 위치: {filepath}")
                                    
                                except Exception as e:
                                    st.error(f"저장 실패: {e}")
                            else:
                                st.warning("스토리 이름을 입력해주세요.")
                    
                    with col_download:
                        st.subheader("📥 파일 다운로드")
                        # 다운로드 버튼
                        st.download_button(
                            label="📥 JSON 파일 다운로드",
                            data=st.session_state.current_game_data,
                            file_name=f"custom_game_{scenario_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
            except json.JSONDecodeError:
                st.error("생성된 데이터가 올바른 JSON 형식이 아닙니다.")
                st.code(st.session_state.current_game_data)
        else:
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
            
            # 예시 요청이 선택된 경우 처리
            if hasattr(st.session_state, 'example_request'):
                user_input = st.session_state.example_request
                delattr(st.session_state, 'example_request')
                
                # 사용자 메시지 추가
                st.session_state.chat_history.append(("user", user_input))
                
                # AI 응답 생성 (위의 로직과 동일)
                with st.spinner("스토리를 생성하고 있습니다..."):
                    try:
                        game_data, analysis = st.session_state.customizer.generate_custom_scenario(
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
    
    # 하단 정보
    st.markdown("---")
    
    # 탭으로 구분된 추가 정보
    info_tab1, info_tab2, info_tab3, info_tab4 = st.tabs(["ℹ️ 사용 방법", "📊 통계", "🎯 팁", "🔧 설정"])
    
    with info_tab1:
        col_help1, col_help2 = st.columns(2)
        
        with col_help1:
            st.markdown("""
            ### 🎯 게임 커스터마이저 사용법
            
            1. **시나리오 선택**: 왼쪽 사이드바에서 원하는 기본 시나리오를 선택하세요
            2. **채팅으로 요청**: 왼쪽 채팅창에 원하는 변경사항을 자연어로 입력하세요
            3. **결과 확인**: 오른쪽에서 생성된 커스텀 스토리를 확인하세요
            4. **저장/다운로드**: 마음에 드는 스토리는 저장하거나 JSON 파일로 다운로드할 수 있습니다
            
            ### 💡 요청 예시
            - **캐릭터 변경**: "주인공을 용감한 기사로 바꿔줘"
            - **배경 변경**: "바다 속 세계로 배경을 바꿔줘"
            - **난이도 조절**: "더 쉬운 단어로 설명해줘"
            - **스토리 추가**: "모험 요소를 더 많이 넣어줘"
            """)
        
        with col_help2:
            st.markdown("""
            ### 🔍 고급 기능
            
            - **의도 분석**: AI가 요청의 의도를 분석하여 최적화된 응답을 제공합니다
            - **품질 검증**: 생성된 스토리의 품질을 자동으로 검증합니다
            - **개선 제안**: AI가 추가 개선 방향을 제안합니다
            - **피드백 반영**: 평가와 피드백을 통해 스토리를 지속적으로 개선할 수 있습니다
            
            ### 💾 저장 관리
            
            - **자동 메타데이터**: 생성일, 사용자 요청 등이 자동으로 저장됩니다
            - **빠른 불러오기**: 사이드바에서 저장된 스토리를 빠르게 불러올 수 있습니다
            - **내보내기**: JSON 파일로 다운로드하여 다른 용도로 사용할 수 있습니다
            """)
    
    with info_tab2:
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
                    st.metric("💾 총 저장된 스토리", len(saved_stories))
                    st.metric("📦 총 데이터 크기", f"{total_size:,} bytes")
                
                with col_saved2:
                    st.write("**시나리오별 분포:**")
                    for scenario, count in scenario_counts.items():
                        st.write(f"• {scenario}: {count}개")
            else:
                st.info("아직 저장된 스토리가 없습니다.")
    
    with info_tab3:
        st.markdown("""
        ### 🎯 효과적인 스토리 커스터마이징 팁
        
        #### 📝 명확한 요청하기
        - "더 재미있게 해줘" → "모험과 액션이 많은 스토리로 만들어줘"
        - "바꿔줘" → "주인공을 공주로 바꿔줘"
        
        #### 🎭 창의적인 아이디어
        - 다양한 배경: 우주, 바다, 정글, 미래 도시 등
        - 특별한 캐릭터: 로봇, 요정, 드래곤, 외계인 등
        - 재미있는 설정: 시간 여행, 마법, 초능력 등
        
        #### 👶 연령 고려사항
        - "5세도 이해할 수 있게" - 더 쉬운 단어 사용
        - "초등학생 수준으로" - 적절한 복잡도 유지
        - "교육적 요소 강화" - 학습 목표 명확화
        
        #### 🔄 반복 개선
        - 생성된 스토리를 평가하고 피드백 제공
        - 구체적인 개선 요청으로 점진적 발전
        - 여러 버전을 만들어 비교해보기
        """)
    
    with info_tab4:
        st.markdown("""
        ### 🔧 고급 설정 및 문제 해결
        
        #### ⚙️ 환경 설정
        - **API 키**: `.env` 파일에 `OPENAI_API_KEY=your_api_key` 형태로 설정
        - **모델 설정**: `utils/config.py`에서 GPT 모델 및 매개변수 조정 가능
        - **저장 위치**: 기본적으로 `saved_stories` 폴더에 저장됨
        
        #### 🔍 문제 해결
        - **API 오류**: API 키가 올바르게 설정되었는지 확인
        - **생성 실패**: 인터넷 연결 및 OpenAI 서비스 상태 확인
        - **저장 실패**: 디렉토리 권한 및 디스크 공간 확인
        
        #### 🚀 성능 최적화
        - 너무 긴 요청은 여러 단계로 나누어 진행
        - 대화 히스토리가 길어지면 초기화하여 성능 향상
        - 복잡한 요청은 단계별로 구체화하여 진행
        """)
        
        # 디버그 정보 (개발자용)
        with st.expander("🔧 디버그 정보 (개발자용)", expanded=False):
            st.write("**세션 상태:**")
            st.write(f"- 채팅 히스토리: {len(getattr(st.session_state, 'chat_history', []))}개")
            st.write(f"- 현재 게임 데이터: {'있음' if getattr(st.session_state, 'current_game_data', None) else '없음'}")
            st.write(f"- 커스터마이저: {'초기화됨' if getattr(st.session_state, 'customizer', None) else '없음'}")
            
            if st.button("🔄 세션 초기화 (모든 데이터 삭제)"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("세션이 초기화되었습니다!")
                st.rerun()

if __name__ == "__main__":
    main()
