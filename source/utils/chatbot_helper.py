"""
고급 챗봇 기능을 위한 헬퍼 모듈
"""
import json
import re
from typing import Dict, List, Optional

class ChatbotHelper:
    """챗봇 대화 및 시나리오 커스터마이징을 위한 헬퍼 클래스"""
    
    def __init__(self):
        self.conversation_context = []
        self.scenario_templates = {
            "magic_kingdom": "마법 왕국",
            "foodtruck_kingdom": "푸드트럭 왕국", 
            "moonlight_thief": "달빛 도둑"
        }
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, any]:
        """사용자 입력을 분석하여 투자 학습 의도를 파악합니다."""
        intent = {
            "type": "general",
            "keywords": [],
            "sentiment": "neutral",
            "investment_focus": [],
            "difficulty_level": "normal"
        }
        
        user_input_lower = user_input.lower()
        
        # 투자 방식별 키워드 분석
        stable_keywords = ["안정", "안전", "리스크", "위험", "보수적", "예금", "적금", "안정형"]
        if any(keyword in user_input_lower for keyword in stable_keywords):
            intent["type"] = "stable_investment"
            intent["investment_focus"].append("안정형 투자")
            intent["keywords"].extend([kw for kw in stable_keywords if kw in user_input_lower])
        
        # 분산투자 관련 키워드
        diversification_keywords = ["분산", "포트폴리오", "여러", "다양한", "골고루", "나누어", "분산투자"]
        if any(keyword in user_input_lower for keyword in diversification_keywords):
            intent["type"] = "diversification"
            intent["investment_focus"].append("분산투자")
            intent["keywords"].extend([kw for kw in diversification_keywords if kw in user_input_lower])
        
        # 매매 타이밍 관련 키워드
        timing_keywords = ["타이밍", "매수", "매도", "사고", "팔고", "언제", "시기", "때", "기회"]
        if any(keyword in user_input_lower for keyword in timing_keywords):
            intent["type"] = "trading_timing"
            intent["investment_focus"].append("매매 타이밍")
            intent["keywords"].extend([kw for kw in timing_keywords if kw in user_input_lower])
        
        # 성장형 투자 관련 키워드
        growth_keywords = ["성장", "수익", "이익", "투자", "주식", "성장형", "공격적"]
        if any(keyword in user_input_lower for keyword in growth_keywords):
            intent["type"] = "growth_investment"
            intent["investment_focus"].append("성장형 투자")
            intent["keywords"].extend([kw for kw in growth_keywords if kw in user_input_lower])
        
        # 난이도 조절 요청 감지
        difficulty_keywords = ["쉽게", "어렵게", "간단하게", "복잡하게", "기초", "고급", "초급", "상급"]
        if any(keyword in user_input_lower for keyword in difficulty_keywords):
            if any(word in user_input_lower for word in ["쉽게", "간단하게", "기초", "초급"]):
                intent["difficulty_level"] = "easy"
            elif any(word in user_input_lower for word in ["어렵게", "복잡하게", "고급", "상급"]):
                intent["difficulty_level"] = "hard"
            intent["keywords"].extend([kw for kw in difficulty_keywords if kw in user_input_lower])
        
        # 감정 분석 (간단한 규칙 기반)
        positive_words = ["좋아", "재미있", "멋진", "훌륭", "완벽", "사랑", "도움", "유용"]
        negative_words = ["싫어", "지루", "별로", "아쉬", "부족", "어려워", "모르겠"]
        
        if any(word in user_input_lower for word in positive_words):
            intent["sentiment"] = "positive"
        elif any(word in user_input_lower for word in negative_words):
            intent["sentiment"] = "negative"
        
        return intent
    
    def generate_response_prompt(self, user_input: str, intent: Dict, base_scenario: str) -> str:
        """사용자 의도에 맞는 투자 교육 응답 프롬프트를 생성합니다."""
        
        base_instruction = f"""
        사용자 요청: "{user_input}"
        감지된 투자 학습 의도: {intent['type']}
        기본 시나리오: {base_scenario}
        
        다음 지침에 따라 투자 교육 게임 시나리오를 수정해주세요:
        """
        
        specific_instructions = {
            "stable_investment": """
            - 안정형 투자의 중요성과 원칙을 강조하는 스토리로 수정하세요
            - 리스크 관리와 안전한 투자 방법을 자연스럽게 학습할 수 있도록 하세요
            - 예금, 적금, 안전자산 등의 개념을 게임 속 아이템이나 상점으로 표현하세요
            - 급하게 투자하지 않고 신중하게 결정하는 것의 중요성을 보여주세요
            """,
            "diversification": """
            - 분산투자의 개념과 중요성을 중심으로 스토리를 수정하세요
            - "계란을 한 바구니에 담지 말라"는 원칙을 게임 상황으로 표현하세요
            - 여러 종류의 투자 상품을 다양하게 구매하는 상황을 만드세요
            - 포트폴리오 구성의 기본 개념을 자연스럽게 학습할 수 있도록 하세요
            """,
            "trading_timing": """
            - 매수와 매도 타이밍의 중요성을 중심으로 스토리를 수정하세요
            - 시장 상황을 관찰하고 적절한 시기를 기다리는 것의 중요성을 보여주세요
            - 감정적 투자가 아닌 합리적 판단의 중요성을 강조하세요
            - 장기 투자 vs 단기 투자의 차이점을 자연스럽게 설명하세요
            """,
            "growth_investment": """
            - 성장형 투자의 특성과 가능성을 중심으로 스토리를 수정하세요
            - 더 높은 수익을 위해서는 더 높은 리스크가 따른다는 점을 보여주세요
            - 기업의 성장 가능성을 판단하는 기준을 게임 요소로 표현하세요
            - 장기적 관점에서의 투자 가치를 강조하세요
            """,
            "general": """
            - 사용자의 요청을 최대한 반영하여 투자 교육 시나리오를 개선하세요
            - 기본적인 경제 개념과 투자 원칙을 자연스럽게 포함하세요
            """
        }
        
        instruction = specific_instructions.get(intent['type'], specific_instructions['general'])
        
        # 난이도 조절 추가
        if intent['difficulty_level'] == 'easy':
            instruction += "\n- 더 쉬운 단어와 간단한 설명으로 수정하세요"
        elif intent['difficulty_level'] == 'hard':
            instruction += "\n- 더 복잡한 투자 개념과 상세한 설명을 포함하세요"
        
        return base_instruction + instruction
    
    def create_conversation_summary(self, chat_history: List[tuple]) -> str:
        """대화 히스토리를 요약합니다."""
        if not chat_history:
            return "새로운 대화입니다."
        
        user_requests = [msg for role, msg in chat_history if role == "user"]
        
        if len(user_requests) <= 3:
            return f"사용자가 요청한 내용: {', '.join(user_requests[-3:])}"
        else:
            return f"최근 요청사항: {', '.join(user_requests[-3:])}"
    
    def validate_generated_content(self, content: str) -> Dict[str, any]:
        """생성된 콘텐츠의 품질을 검증합니다."""
        validation_result = {
            "is_valid": False,
            "is_json": False,
            "has_required_fields": False,
            "is_child_friendly": True,
            "issues": []
        }
        
        try:
            # JSON 형식 검증
            parsed_content = json.loads(content)
            validation_result["is_json"] = True
            
            # 필수 필드 검증
            if isinstance(parsed_content, list) and len(parsed_content) > 0:
                first_item = parsed_content[0]
                required_fields = ["day", "situation", "shops"]
                
                if all(field in first_item for field in required_fields):
                    validation_result["has_required_fields"] = True
            
            # 아동 친화적 내용 검증 (간단한 규칙)
            inappropriate_words = ["폭력", "위험한", "무서운", "죽음", "전쟁"]
            content_lower = content.lower()
            
            for word in inappropriate_words:
                if word in content_lower:
                    validation_result["is_child_friendly"] = False
                    validation_result["issues"].append(f"부적절한 단어 발견: {word}")
            
            # 전체 유효성 판단
            validation_result["is_valid"] = (
                validation_result["is_json"] and 
                validation_result["has_required_fields"] and 
                validation_result["is_child_friendly"]
            )
            
        except json.JSONDecodeError:
            validation_result["issues"].append("유효하지 않은 JSON 형식")
        except Exception as e:
            validation_result["issues"].append(f"검증 중 오류: {str(e)}")
        
        return validation_result
    
    def suggest_improvements(self, user_input: str, current_scenario: str) -> List[str]:
        """사용자 입력을 바탕으로 투자 학습 개선 제안을 생성합니다."""
        suggestions = []
        
        user_input_lower = user_input.lower()
        
        # 투자 방식별 구체적인 제안들
        if "안정" in user_input_lower or "안전" in user_input_lower:
            suggestions.append("💰 예금과 적금의 차이점 설명 추가")
            suggestions.append("📊 리스크와 수익률의 관계 학습")
            suggestions.append("🛡️ 안전자산의 종류와 특징 소개")
        
        elif "분산" in user_input_lower or "포트폴리오" in user_input_lower:
            suggestions.append("🥚 계란 바구니 비유로 분산투자 설명")
            suggestions.append("📈 다양한 투자 상품 조합 연습")
            suggestions.append("⚖️ 자산 배분의 기본 원칙 학습")
        
        elif "타이밍" in user_input_lower or "매수" in user_input_lower or "매도" in user_input_lower:
            suggestions.append("⏰ 시장 타이밍의 어려움과 대안 설명")
            suggestions.append("📅 정기 투자의 장점 학습")
            suggestions.append("💭 감정적 투자 vs 합리적 투자")
        
        elif "쉽" in user_input_lower:
            suggestions.append("📚 더 간단한 단어로 설명")
            suggestions.append("🖼️ 시각적 요소나 이모지 추가")
            suggestions.append("👶 연령에 맞는 예시 사용")
        
        else:
            # 일반적인 투자 교육 개선 제안
            suggestions = [
                "💡 실생활 예시로 투자 개념 설명",
                "🎯 명확한 학습 목표와 성취감 제공",
                "🔄 반복 학습을 통한 개념 정착"
            ]
        
        return suggestions[:3]  # 최대 3개까지만 반환
