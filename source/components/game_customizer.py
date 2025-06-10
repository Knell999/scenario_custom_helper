"""
스토리 편집 컴포넌트 - 기존 스토리 수정 전용
"""
import streamlit as st
import json
import os
from source.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
from source.utils.prompts import get_system_prompt, get_story_modification_prompt
from source.components.story_editor import StoryEditor
from source.utils.chatbot_helper import ChatbotHelper
import os
from typing import List, Dict


class GameCustomizer:
    def __init__(self):
        """스토리 편집기 초기화"""
        self.llm = None
        self.story_editor = StoryEditor()
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
    
    def modify_existing_story(self, story_name: str, user_request: str, chat_history=None):
        """기존 스토리를 사용자 요청에 따라 수정"""
        if not self.llm:
            return None, {"error": "LLM 모델이 초기화되지 않았습니다. 설정을 확인해주세요."}
        
        # 현재 세션에 로드된 스토리 데이터 사용
        import streamlit as st
        original_story = st.session_state.get('current_game_data')
        
        # 세션 데이터가 없으면 파일에서 로드 시도
        if not original_story:
            original_story = self.story_editor.load_story(story_name)
            if not original_story:
                return None, {"error": f"'{story_name}' 스토리를 찾을 수 없습니다. 파일이 존재하는지 확인해주세요."}
        
        try:
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
                    # JSON 파싱 시도
                    if isinstance(modified_story_data, str):
                        parsed_data = json.loads(modified_story_data)
                    else:
                        parsed_data = modified_story_data
                    
                    # 데이터 타입 확인 및 보정
                    if not isinstance(parsed_data, list):
                        # 만약 딕셔너리에서 'story_data' 키가 있다면 추출
                        if isinstance(parsed_data, dict) and 'story_data' in parsed_data:
                            parsed_data = parsed_data['story_data']
                        else:
                            analysis_result["validation"] = {
                                "is_valid": False,
                                "issues": ["스토리 데이터는 리스트 형태여야 합니다."]
                            }
                            return modified_story_data, analysis_result
                    
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
            
        except Exception as e:
            return None, {"error": f"스토리 수정 중 오류가 발생했습니다: {str(e)}"}
    
    
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
    
    def get_available_stories(self) -> List[str]:
        """GameCustomizer에서 사용할 수 있는 스토리 목록을 반환합니다."""
        return self.story_editor.get_available_stories()
    
    def debug_story_info(self, story_name: str) -> Dict:
        """스토리 디버깅 정보를 반환합니다."""
        import streamlit as st
        
        debug_info = {
            "requested_story_name": story_name,
            "session_has_game_data": bool(st.session_state.get('current_game_data')),
            "session_story_name": st.session_state.get('current_story_name'),
            "available_stories": self.story_editor.get_available_stories(),
            "stories_dir_exists": os.path.exists(self.story_editor.stories_dir),
            "stories_dir_files": []
        }
        
        try:
            if os.path.exists(self.story_editor.stories_dir):
                debug_info["stories_dir_files"] = [f for f in os.listdir(self.story_editor.stories_dir) if f.endswith('.json')]
        except:
            pass
            
        return debug_info
