"""
스토리 저장 및 관리 모듈
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class StoryManager:
    """생성된 스토리를 저장하고 관리하는 클래스"""
    
    def __init__(self, storage_dir: str = "saved_stories"):
        self.storage_dir = storage_dir
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """저장 디렉토리가 존재하는지 확인하고 없으면 생성"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def save_story(self, story_data: str, story_name: str, scenario_type: str, 
                   user_requests: List[str] = None) -> str:
        """
        스토리를 파일로 저장합니다.
        
        Args:
            story_data: JSON 형태의 스토리 데이터
            story_name: 사용자가 지정한 스토리 이름
            scenario_type: 시나리오 타입
            user_requests: 사용자 요청 히스토리
            
        Returns:
            str: 저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{story_name}_{scenario_type}_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # 메타데이터와 함께 저장
        story_with_metadata = {
            "metadata": {
                "story_name": story_name,
                "scenario_type": scenario_type,
                "created_at": datetime.now().isoformat(),
                "user_requests": user_requests or []
            },
            "story_data": json.loads(story_data) if isinstance(story_data, str) else story_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story_with_metadata, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_story(self, filepath: str) -> Dict:
        """저장된 스토리를 불러옵니다."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"스토리 로드 실패: {e}")
    
    def get_saved_stories(self) -> List[Dict]:
        """저장된 모든 스토리의 메타데이터를 반환합니다."""
        stories = []
        
        if not os.path.exists(self.storage_dir):
            return stories
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    story = self.load_story(filepath)
                    story_info = {
                        "filename": filename,
                        "filepath": filepath,
                        "metadata": story.get("metadata", {}),
                        "size": len(str(story.get("story_data", [])))
                    }
                    stories.append(story_info)
                except:
                    continue
        
        # 생성 시간 순으로 정렬 (최신 먼저)
        stories.sort(key=lambda x: x["metadata"].get("created_at", ""), reverse=True)
        return stories
    
    def delete_story(self, filepath: str) -> bool:
        """저장된 스토리를 삭제합니다."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False
