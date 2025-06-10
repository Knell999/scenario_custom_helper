"""
고급 챗봇 기능을 위한 헬퍼 모듈
"""
import json
import re
from typing import Dict, List, Optional

class ChatbotHelper:
    """스토리 편집 챗봇을 위한 대화 컨텍스트 관리 및 요청 분석 헬퍼 클래스"""
    
    def __init__(self):
        self.conversation_context = []
        self.modification_history = []  # 수정 이력 추적
        self.scenario_templates = {
            "magic_kingdom": "마법 왕국",
            "foodtruck_kingdom": "푸드트럭 왕국", 
            "moonlight_thief": "달빛 도둑"
        }
        # 스토리 편집 컨텍스트 추가
        self.current_story_context = {
            "story_name": None,
            "modification_count": 0,
            "last_modification_type": None,
            "user_preferences": {}
        }
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, any]:
        """사용자 입력을 분석하여 스토리 편집 의도를 파악합니다."""
        intent = {
            "type": "general",
            "keywords": [],
            "sentiment": "neutral",
            "modification_scope": "specific",  # specific, general, all
            "target_element": None,  # character, setting, event, dialogue
            "difficulty_level": "normal"
        }
        
        user_input_lower = user_input.lower()
        
        # 스토리 편집 의도 분석 (투자 교육보다는 스토리 편집에 집중)
        character_keywords = ["캐릭터", "인물", "이름", "성격", "주인공", "등장인물"]
        if any(keyword in user_input_lower for keyword in character_keywords):
            intent["type"] = "character_modification"
            intent["target_element"] = "character"
            intent["keywords"].extend([kw for kw in character_keywords if kw in user_input_lower])
        
        # 배경/설정 수정
        setting_keywords = ["배경", "장소", "환경", "설정", "세계관", "왕국", "무대"]
        if any(keyword in user_input_lower for keyword in setting_keywords):
            intent["type"] = "setting_modification"
            intent["target_element"] = "setting"
            intent["keywords"].extend([kw for kw in setting_keywords if kw in user_input_lower])
        
        # 이벤트/사건 수정
        event_keywords = ["이벤트", "사건", "일어나", "발생", "상황", "뉴스", "턴"]
        if any(keyword in user_input_lower for keyword in event_keywords):
            intent["type"] = "event_modification"
            intent["target_element"] = "event"
            intent["keywords"].extend([kw for kw in event_keywords if kw in user_input_lower])
        
        # 대화/텍스트 수정
        dialogue_keywords = ["대화", "대사", "말", "텍스트", "설명", "문장", "표현"]
        if any(keyword in user_input_lower for keyword in dialogue_keywords):
            intent["type"] = "dialogue_modification"
            intent["target_element"] = "dialogue"
            intent["keywords"].extend([kw for kw in dialogue_keywords if kw in user_input_lower])
        
        # 수정 범위 분석
        if any(word in user_input_lower for word in ["전체", "모든", "모두", "다"]):
            intent["modification_scope"] = "all"
        elif any(word in user_input_lower for word in ["특정", "이 부분", "여기", "이것"]):
            intent["modification_scope"] = "specific"
        
        # 특정 턴 분석
        for i in range(1, 11):
            if f"{i}턴" in user_input_lower or f"{i}일" in user_input_lower:
                intent["target_turn"] = i
                intent["modification_scope"] = "specific"
                break
        
        # 난이도 조절 요청 감지
        difficulty_keywords = ["쉽게", "어렵게", "간단하게", "복잡하게", "기초", "고급", "초급", "상급"]
        if any(keyword in user_input_lower for keyword in difficulty_keywords):
            if any(word in user_input_lower for word in ["쉽게", "간단하게", "기초", "초급"]):
                intent["difficulty_level"] = "easy"
            elif any(word in user_input_lower for word in ["어렵게", "복잡하게", "고급", "상급"]):
                intent["difficulty_level"] = "hard"
            intent["keywords"].extend([kw for kw in difficulty_keywords if kw in user_input_lower])
        
        # 감정 분석 (간단한 규칙 기반)
        positive_words = ["좋아", "재미있", "멋진", "훌륭", "완벽", "사랑", "도움", "유용", "더 좋게", "개선"]
        negative_words = ["싫어", "지루", "별로", "아쉬", "부족", "어려워", "모르겠", "이상해"]
        
        if any(word in user_input_lower for word in positive_words):
            intent["sentiment"] = "positive"
        elif any(word in user_input_lower for word in negative_words):
            intent["sentiment"] = "negative"
        
        return intent
    
    def generate_response_prompt(self, user_input: str, intent: Dict, base_scenario: str) -> str:
        """사용자 의도에 맞는 스토리 편집 응답 프롬프트를 생성합니다."""
        
        base_instruction = f"""
        사용자 요청: "{user_input}"
        감지된 스토리 편집 의도: {intent['type']}
        기본 시나리오: {base_scenario}
        
        다음 지침에 따라 게임 스토리를 수정해주세요:
        """
        
        specific_instructions = {
            "character_modification": """
            - 캐릭터의 성격, 외모, 능력, 대사 등을 더 생동감 있고 매력적으로 수정하세요
            - 캐릭터 간의 상호작용과 관계를 더 흥미롭게 만드세요
            - 각 캐릭터만의 개성과 특징을 명확하게 드러내세요
            - 플레이어가 캐릭터에게 감정적으로 몰입할 수 있도록 하세요
            """,
            "setting_modification": """
            - 배경 설정을 더 상세하고 매력적으로 묘사하세요
            - 스토리의 분위기와 톤에 맞는 환경을 조성하세요
            - 각 장소가 가진 고유한 특색과 의미를 부여하세요
            - 플레이어의 상상력을 자극하는 생생한 묘사를 추가하세요
            """,
            "event_modification": """
            - 이벤트를 더 흥미진진하고 참여하고 싶게 만드세요
            - 예상치 못한 전개와 놀라운 결과를 추가하세요
            - 플레이어의 선택이 결과에 미치는 영향을 명확히 하세요
            - 재미있고 기억에 남을 만한 상황을 연출하세요
            """,
            "dialogue_modification": """
            - 대화를 더 자연스럽고 생동감 있게 수정하세요
            - 각 캐릭터의 말투와 성격이 잘 드러나도록 하세요
            - 유머나 감동적인 요소를 적절히 포함하세요
            - 플레이어가 몰입할 수 있는 대화 흐름을 만드세요
            """,
            "general": """
            - 사용자의 요청을 최대한 반영하여 스토리를 개선하세요
            - 더 재미있고 매력적인 게임 경험을 제공하도록 수정하세요
            - 스토리의 일관성과 몰입감을 유지하세요
            """
        }
        
        instruction = specific_instructions.get(intent['type'], specific_instructions['general'])
        
        # 특정 턴 수정 요청 처리
        if 'target_turn' in intent:
            instruction += f"\n- 특히 {intent['target_turn']}턴의 내용을 중점적으로 개선하세요"
        
        # 수정 범위에 따른 지침
        if intent['modification_scope'] == 'all':
            instruction += "\n- 전체 스토리의 톤과 분위기를 일관되게 수정하세요"
        elif intent['modification_scope'] == 'specific':
            instruction += "\n- 지정된 부분에 집중하되 전체 스토리와의 연결성을 유지하세요"
        
        # 난이도 조절 추가
        if intent['difficulty_level'] == 'easy':
            instruction += "\n- 더 쉬운 단어와 간단한 설명으로 수정하세요"
        elif intent['difficulty_level'] == 'hard':
            instruction += "\n- 더 복잡하고 깊이 있는 스토리 요소를 포함하세요"
        
        return base_instruction + instruction
    
    def create_conversation_summary(self, chat_history: List[tuple]) -> str:
        """대화 히스토리를 요약합니다."""
        if not chat_history:
            return "새로운 스토리 편집 세션입니다."
        
        user_requests = [msg for role, msg in chat_history if role == "user"]
        
        if len(user_requests) <= 3:
            return f"사용자가 요청한 스토리 수정 내용: {', '.join(user_requests[-3:])}"
        else:
            return f"최근 스토리 수정 요청사항: {', '.join(user_requests[-3:])}"
    
    def validate_generated_content(self, content: str) -> Dict[str, any]:
        """생성된 스토리 콘텐츠의 품질을 검증합니다."""
        validation_result = {
            "is_valid": False,
            "is_json": False,
            "has_required_fields": False,
            "is_story_appropriate": True,
            "issues": []
        }
        
        try:
            # JSON 형식 검증
            parsed_content = json.loads(content)
            validation_result["is_json"] = True
            
            # 필수 필드 검증 (스토리 구조)
            if isinstance(parsed_content, list) and len(parsed_content) > 0:
                first_item = parsed_content[0]
                required_fields = ["turn_number", "result", "news", "stocks"]
                
                if all(field in first_item for field in required_fields):
                    validation_result["has_required_fields"] = True
            
            # 스토리 적절성 검증 (아동 친화적 내용)
            inappropriate_words = ["폭력", "위험한", "무서운", "죽음", "전쟁", "혈액", "살인"]
            content_lower = content.lower()
            
            for word in inappropriate_words:
                if word in content_lower:
                    validation_result["is_story_appropriate"] = False
                    validation_result["issues"].append(f"부적절한 내용 발견: {word}")
            
            # 스토리 일관성 검증 (기본적인 체크)
            if validation_result["is_json"] and validation_result["has_required_fields"]:
                for item in parsed_content:
                    if not item.get("result") or len(item.get("result", "")) < 10:
                        validation_result["issues"].append("스토리 설명이 너무 짧습니다")
                    
                    stocks = item.get("stocks", [])
                    if not stocks or len(stocks) == 0:
                        validation_result["issues"].append("주식 정보가 누락되었습니다")
            
            # 전체 유효성 판단
            validation_result["is_valid"] = (
                validation_result["is_json"] and 
                validation_result["has_required_fields"] and 
                validation_result["is_story_appropriate"] and
                len(validation_result["issues"]) == 0
            )
            
        except json.JSONDecodeError:
            validation_result["issues"].append("유효하지 않은 JSON 형식")
        except Exception as e:
            validation_result["issues"].append(f"검증 중 오류: {str(e)}")
        
        return validation_result
    
    def suggest_improvements(self, user_input: str, current_scenario: str) -> List[str]:
        """사용자 입력을 바탕으로 스토리 편집 개선 제안을 생성합니다."""
        suggestions = []
        
        user_input_lower = user_input.lower()
        
        # 스토리 요소별 구체적인 제안들
        if any(keyword in user_input_lower for keyword in ["캐릭터", "인물", "등장인물"]):
            suggestions.append("👥 캐릭터의 개성과 배경 스토리 추가")
            suggestions.append("💬 캐릭터 간의 대화와 상호작용 강화")
            suggestions.append("🎭 각 캐릭터만의 독특한 말투와 특징 부여")
        
        elif any(keyword in user_input_lower for keyword in ["배경", "장소", "환경", "설정"]):
            suggestions.append("🏰 더 생생하고 상세한 배경 묘사")
            suggestions.append("🌟 각 장소만의 특별한 분위기 연출")
            suggestions.append("🗺️ 스토리와 연결된 의미 있는 공간 설계")
        
        elif any(keyword in user_input_lower for keyword in ["이벤트", "사건", "상황"]):
            suggestions.append("🎪 예상치 못한 재미있는 반전 추가")
            suggestions.append("🎯 플레이어 선택의 결과가 명확한 이벤트")
            suggestions.append("🎲 흥미진진한 도전과 보상 시스템")
        
        elif any(keyword in user_input_lower for keyword in ["대화", "대사", "텍스트"]):
            suggestions.append("💭 자연스럽고 몰입감 있는 대화")
            suggestions.append("😄 유머와 감동을 적절히 조화")
            suggestions.append("🎪 캐릭터 성격이 잘 드러나는 말투")
        
        elif any(keyword in user_input_lower for keyword in ["재미있", "흥미", "재밌"]):
            suggestions.append("🎉 더 다이나믹하고 활기찬 상황 연출")
            suggestions.append("🎨 창의적이고 독특한 아이디어 추가")
            suggestions.append("🎯 플레이어의 호기심을 자극하는 요소")
        
        elif any(keyword in user_input_lower for keyword in ["쉽", "간단"]):
            suggestions.append("📚 더 이해하기 쉬운 설명과 표현")
            suggestions.append("🖼️ 시각적 요소나 이모지 활용")
            suggestions.append("👶 연령에 맞는 친근한 예시 사용")
        
        else:
            # 일반적인 스토리 개선 제안
            suggestions = [
                "✨ 더 매력적이고 몰입감 있는 스토리텔링",
                "🎮 플레이어 참여도를 높이는 상호작용 요소",
                "🌈 다양하고 풍부한 감정 표현과 분위기"
            ]
        
        return suggestions[:3]  # 최대 3개까지만 반환
    
    def update_story_context(self, story_name: str, modification_type: str, user_preferences: Dict = None):
        """현재 스토리 편집 컨텍스트를 업데이트합니다."""
        self.current_story_context["story_name"] = story_name
        self.current_story_context["modification_count"] += 1
        self.current_story_context["last_modification_type"] = modification_type
        
        if user_preferences:
            self.current_story_context["user_preferences"].update(user_preferences)
        
        # 수정 이력에 추가
        self.modification_history.append({
            "story_name": story_name,
            "modification_type": modification_type,
            "timestamp": None,  # 실제 구현시 datetime 추가
            "preferences": user_preferences or {}
        })
    
    def get_story_editing_tips(self, story_type: str) -> List[str]:
        """스토리 타입별 편집 팁을 제공합니다."""
        tips_by_type = {
            "magic_kingdom": [
                "🪄 마법 요소를 창의적으로 활용하여 흥미로운 상황 연출",
                "👑 왕국의 정치적 상황이나 사회적 배경 활용",
                "✨ 신비로운 분위기와 모험적 요소의 조화"
            ],
            "foodtruck_kingdom": [
                "🍕 다양한 음식과 요리 과정을 스토리에 자연스럽게 연결",
                "🚚 이동하는 푸드트럭의 특성을 활용한 다양한 만남",
                "😋 음식을 통한 따뜻한 인간관계와 소통 강조"
            ],
            "moonlight_thief": [
                "🌙 밤의 신비로운 분위기와 은밀한 액션의 조화",
                "🔍 추리와 모험 요소를 통한 긴장감 연출",
                "💎 도둑이지만 매력적인 캐릭터로 표현"
            ]
        }
        
        return tips_by_type.get(story_type, [
            "📖 일관된 스토리 흐름과 캐릭터 발전",
            "🎯 명확한 목표와 동기 부여",
            "🌟 독창적이고 기억에 남을 만한 요소"
        ])
