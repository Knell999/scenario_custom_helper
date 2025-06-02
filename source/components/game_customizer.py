"""
게임 커스터마이저 컴포넌트
"""
import streamlit as st
from source.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
from source.utils.prompts import get_system_prompt, get_game_scenario_prompt
from source.utils.chatbot_helper import ChatbotHelper


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
