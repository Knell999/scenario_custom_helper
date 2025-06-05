"""
게임 커스터마이저 컴포넌트 - 기존 스토리 수정 기능 포함
"""
import streamlit as st
import json
from source.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
from source.utils.prompts import get_system_prompt, get_story_modification_prompt, get_game_scenario_prompt
from source.utils.chatbot_helper import ChatbotHelper
from source.components.story_editor import StoryEditor


class GameCustomizer:
    def __init__(self):
        """게임 커스터마이저 초기화"""
        self.llm = None
        self.chatbot_helper = ChatbotHelper()
        self.story_editor = StoryEditor()
        self.initialize_llm_model()
        
    def initialize_llm_model(self):
        """LLM 모델 초기화"""
        try:
            self.llm = initialize_llm()
            return True
        except Exception as e:
            st.error(f"LLM 모델 초기화 실패: {e}")
            return False
    
    def modify_existing_story(self, story_name: str, user_request: str, chat_history=None):
        """기존 스토리를 사용자 요청에 따라 수정"""
        if not self.llm:
            return None, None
            
        # 기존 스토리 로드
        original_story = self.story_editor.load_story(story_name)
        if not original_story:
            return None, {"error": "스토리를 찾을 수 없습니다."}
        
        # 수정 요청 분석
        modification_analysis = self.story_editor.analyze_modification_request(user_request)
        
        # 대화 컨텍스트 포함
        conversation_summary = self.chatbot_helper.create_conversation_summary(chat_history or [])
        
        # 스토리 수정을 위한 프롬프트 생성
        story_json = json.dumps(original_story, ensure_ascii=False, indent=2)
        modification_prompt = get_story_modification_prompt(
            story_json, user_request, modification_analysis['type']
        )
        
        # 프롬프트 템플릿 생성
        prompt_template = create_prompt_template(get_system_prompt())
        
        # 수정된 스토리 생성
        modified_story_data = generate_game_data(self.llm, prompt_template, modification_prompt)
        
        # 수정된 스토리 검증
        analysis_result = {
            "intent": {
                "type": modification_analysis['type'],
                "target_turn": modification_analysis.get('target_turn'),
                "confidence": 0.9
            },
            "validation": None,
            "suggestions": []
        }
        
        if modified_story_data:
            try:
                parsed_data = json.loads(modified_story_data)
                is_valid, errors = self.story_editor.validate_story_structure(parsed_data)
                analysis_result["validation"] = {
                    "is_valid": is_valid,
                    "issues": errors if not is_valid else []
                }
                
                if is_valid:
                    # 수정된 스토리 저장
                    self.story_editor.save_modified_story(parsed_data, story_name)
                    analysis_result["suggestions"] = [
                        "스토리가 성공적으로 수정되었습니다.",
                        "다른 부분도 수정하고 싶으시면 말씀해주세요."
                    ]
                
            except json.JSONDecodeError:
                analysis_result["validation"] = {
                    "is_valid": False,
                    "issues": ["생성된 데이터가 유효한 JSON 형식이 아닙니다."]
                }
        
        return modified_story_data, analysis_result
    
    def get_story_summary(self, story_name: str):
        """스토리 요약 정보 반환"""
        story_data = self.story_editor.load_story(story_name)
        if not story_data:
            return None
        
        # 스토리 데이터 분석
        summary = {
            'total_turns': len(story_data) if isinstance(story_data, list) else 0,
            'characters': [],
            'last_modified': 'Unknown'
        }
        
        # 캐릭터 추출
        all_chars = set()
        if isinstance(story_data, list):
            for turn in story_data:
                if 'stocks' in turn:
                    for stock in turn['stocks']:
                        name = stock.get('name', '')
                        if name:
                            all_chars.add(name)
        summary['characters'] = list(all_chars)
        
        return summary
    
    def get_available_stories(self):
        """사용 가능한 스토리 목록 반환"""
        return self.story_editor.get_available_stories()

    def generate_custom_scenario(self, user_input, scenario_type="magic_kingdom", chat_history=None):
        """기존 방식 유지 - 새로운 시나리오 생성 (하위 호환성)"""
        # 기존 스토리가 선택된 경우 수정 모드로 동작
        if hasattr(st.session_state, 'selected_story') and st.session_state.selected_story:
            return self.modify_existing_story(st.session_state.selected_story, user_input, chat_history)
        
        # 기존 로직 유지 (새로운 스토리 생성)
        if not self.llm:
            return None, None
            
        # 사용자 의도 분석
        intent = self.chatbot_helper.analyze_user_intent(user_input)
        
        # 대화 컨텍스트 포함
        conversation_summary = self.chatbot_helper.create_conversation_summary(chat_history or [])
        
        # 커스터마이징을 위한 프롬프트 생성
        from source.utils.prompts import get_game_scenario_prompt
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
        
        # 세션 상태에서 투자 포커스 가져오기
        investment_focus = getattr(st.session_state, 'investment_focus', 'stable_investment')
        
        customization_instruction = f"""
        기본 시나리오: {scenario_type}
        투자 학습 포커스: {investment_focus}
        
        대화 컨텍스트: {conversation_summary}
        
        사용자의 현재 요청: {user_input}
        감지된 의도: {intent['type']}
        관련 키워드: {', '.join(intent['keywords'])}
        사용자 감정: {intent['sentiment']}
        
        {self.chatbot_helper.generate_response_prompt(user_input, intent, scenario_type)}
        
        중요 지침:
        1. 10세 이하 아동이 이해하기 쉬운 언어 사용
        2. 투자와 돈 관리의 기본 개념을 자연스럽게 학습할 수 있도록 구성
        3. 선택된 투자 방식({investment_focus})에 특화된 학습 요소 강화
        4. 재미있고 흥미로운 스토리텔링 요소 포함
        5. 안전하고 교육적인 내용으로 구성
        6. JSON 형식으로 정확히 출력
        7. 캐릭터나 배경 변경보다는 투자 개념 학습에 집중
        
        기본 시나리오 참고:
        {base_prompt}
        """
        
        return customization_instruction
