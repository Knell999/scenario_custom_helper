"""
스토리 편집 매니저 - 기존 스토리 데이터 수정 및 관리
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class StoryEditor:
    def __init__(self, stories_dir="saved_stories"):
        """스토리 편집기 초기화"""
        self.stories_dir = stories_dir
        self.current_story = None
        self.current_story_name = None
        
    def load_story(self, story_name: str) -> Optional[Dict]:
        """저장된 스토리 파일을 로드합니다."""
        try:
            story_path = os.path.join(self.stories_dir, f"{story_name}.json")
            if os.path.exists(story_path):
                with open(story_path, 'r', encoding='utf-8') as f:
                    story_data = json.load(f)
                self.current_story = story_data
                self.current_story_name = story_name
                return story_data
            return None
        except Exception as e:
            print(f"스토리 로드 실패: {e}")
            return None
            
    def list_available_stories(self) -> List[str]:
        """사용 가능한 스토리 목록을 반환합니다."""
        try:
            if not os.path.exists(self.stories_dir):
                return []
            
            stories = []
            for file in os.listdir(self.stories_dir):
                if file.endswith('.json'):
                    story_name = file.replace('.json', '')
                    stories.append(story_name)
            return sorted(stories)
        except Exception as e:
            print(f"스토리 목록 로드 실패: {e}")
            return []
            
    def get_available_stories(self) -> List[str]:
        """사용 가능한 스토리 목록을 반환합니다. (GameCustomizer 호환성을 위한 메서드)"""
        return self.list_available_stories()
    
    def get_story_summary(self, story_data: Dict) -> Dict:
        """스토리 데이터의 요약 정보를 반환합니다."""
        try:
            if not story_data or not isinstance(story_data, list):
                return {}
                
            total_turns = len(story_data)
            characters = set()
            locations = set()
            
            # 첫 번째 턴에서 기본 정보 추출
            if total_turns > 0:
                first_turn = story_data[0]
                if 'stocks' in first_turn:
                    for stock in first_turn['stocks']:
                        characters.add(stock.get('name', ''))
                        
            return {
                'total_turns': total_turns,
                'characters': list(characters),
                'locations': list(locations),
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"스토리 요약 생성 실패: {e}")
            return {}
    
    def analyze_modification_request(self, user_request: str) -> Dict:
        """사용자의 수정 요청을 분석합니다."""
        request_lower = user_request.lower()
        
        modification_type = "general"
        target_elements = []
        
        # 수정 유형 분석
        if any(word in request_lower for word in ['캐릭터', '인물', '이름', '성격']):
            modification_type = "character"
            
        elif any(word in request_lower for word in ['배경', '장소', '환경', '설정']):
            modification_type = "setting" 
            
        elif any(word in request_lower for word in ['이벤트', '사건', '뉴스', '주식']):
            modification_type = "events"
            
        elif any(word in request_lower for word in ['대화', '대사', '말', '텍스트']):
            modification_type = "dialogue"
        
        # 특정 턴 지정 확인
        target_turn = None
        for i in range(1, 11):  # 1-10턴 확인
            if f"{i}턴" in request_lower or f"{i}일" in request_lower:
                target_turn = i
                break
                
        return {
            'type': modification_type,
            'target_turn': target_turn,
            'target_elements': target_elements,
            'original_request': user_request
        }
    
    def save_modified_story(self, modified_story_data: Dict, story_name: str = None) -> bool:
        """수정된 스토리를 저장합니다."""
        try:
            if not story_name:
                story_name = self.current_story_name
                
            if not story_name:
                story_name = f"modified_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 백업 생성
            self.create_backup(story_name)
            
            # 수정된 스토리 저장
            story_path = os.path.join(self.stories_dir, f"{story_name}.json")
            with open(story_path, 'w', encoding='utf-8') as f:
                json.dump(modified_story_data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"스토리 저장 실패: {e}")
            return False
    
    def create_backup(self, story_name: str) -> bool:
        """기존 스토리의 백업을 생성합니다."""
        try:
            original_path = os.path.join(self.stories_dir, f"{story_name}.json")
            if os.path.exists(original_path):
                backup_name = f"{story_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = os.path.join(self.stories_dir, backup_name)
                
                with open(original_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            return True
        except Exception as e:
            print(f"백업 생성 실패: {e}")
            return False
    
    def validate_story_structure(self, story_data: Dict) -> Tuple[bool, List[str]]:
        """스토리 데이터의 구조가 유효한지 검증합니다."""
        errors = []
        
        try:
            if not isinstance(story_data, list):
                errors.append("스토리 데이터는 리스트 형태여야 합니다.")
                return False, errors
            
            required_fields = ['turn', 'result', 'news', 'stocks']
            
            for i, turn_data in enumerate(story_data):
                turn_num = i + 1
                
                # 필수 필드 확인
                for field in required_fields:
                    if field not in turn_data:
                        errors.append(f"{turn_num}턴에 '{field}' 필드가 없습니다.")
                
                # 주식 데이터 확인
                if 'stocks' in turn_data and isinstance(turn_data['stocks'], list):
                    for j, stock in enumerate(turn_data['stocks']):
                        if not isinstance(stock, dict):
                            errors.append(f"{turn_num}턴 {j+1}번째 주식 데이터가 유효하지 않습니다.")
                        else:
                            stock_required = ['name', 'current_value', 'risk_level']
                            for field in stock_required:
                                if field not in stock:
                                    errors.append(f"{turn_num}턴 주식 '{stock.get('name', 'Unknown')}'에 '{field}' 필드가 없습니다.")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"구조 검증 중 오류 발생: {e}")
            return False, errors
