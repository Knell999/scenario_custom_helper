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
        
        # 파일명 안전하게 처리 (특수문자 제거/변환)
        safe_story_name = self._sanitize_filename(story_name)
        safe_scenario_type = self._sanitize_filename(scenario_type)
        
        filename = f"story_{safe_story_name}_{safe_scenario_type}_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # 메타데이터와 함께 저장
        story_with_metadata = {
            "metadata": {
                "story_name": story_name,  # 원본 제목 유지
                "scenario_type": scenario_type,
                "created_at": datetime.now().isoformat(),
                "user_requests": user_requests or [],
                "version": "1.0",
                "is_modified": True if user_requests else False
            },
            "story_data": json.loads(story_data) if isinstance(story_data, str) else story_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story_with_metadata, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _sanitize_filename(self, name: str) -> str:
        """파일명에 안전한 문자열로 변환합니다."""
        # 특수문자를 언더스코어로 변환하고 공백 제거
        import re
        safe_name = re.sub(r'[^\w\s-]', '_', name)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        safe_name = safe_name.strip('_')
        return safe_name[:50]  # 파일명 길이 제한
        
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
            if filename.endswith('.json') and not filename.startswith('.'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    story = self.load_story(filepath)
                    
                    # 파일 크기 계산
                    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    
                    # 새로운 메타데이터 형식과 기존 배열 형식 모두 지원
                    if isinstance(story, dict) and "metadata" in story:
                        # 새로운 형식: 메타데이터가 있는 경우
                        story_info = {
                            "filename": filename,
                            "filepath": filepath,
                            "metadata": story["metadata"],
                            "size": file_size
                        }
                    elif isinstance(story, list):
                        # 기존 형식: 게임 데이터 배열인 경우
                        # 파일명에서 스토리 정보 추출
                        story_info = self._extract_story_info_from_filename(filename, filepath, file_size)
                    else:
                        # 알 수 없는 형식
                        continue
                    
                    stories.append(story_info)
                except Exception as e:
                    # 파일을 읽을 수 없는 경우 건너뛰기
                    print(f"스토리 파일 읽기 실패: {filename}, 오류: {e}")
                    continue
        
        # 생성 시간 순으로 정렬 (최신 먼저)
        stories.sort(key=lambda x: x["metadata"].get("created_at", ""), reverse=True)
        return stories
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """파일명에서 타임스탬프를 추출하여 ISO 형식으로 변환합니다."""
        try:
            # game_scenario_[type]_[YYYYMMDD]_[HHMMSS].json 형식에서 타임스탬프 추출
            filename_parts = filename.replace('.json', '').split('_')
            if len(filename_parts) >= 2:
                # 마지막 두 부분이 날짜와 시간
                date_part = filename_parts[-2]  # YYYYMMDD
                time_part = filename_parts[-1]  # HHMMSS
                
                if len(date_part) == 8 and len(time_part) == 6:
                    # 날짜 형식 변환: YYYYMMDD -> YYYY-MM-DD
                    year = date_part[:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    
                    # 시간 형식 변환: HHMMSS -> HH:MM:SS
                    hour = time_part[:2]
                    minute = time_part[2:4]
                    second = time_part[4:6]
                    
                    return f"{year}-{month}-{day}T{hour}:{minute}:{second}"
        except:
            pass
        
        return ""

    def _extract_story_info_from_filename(self, filename: str, filepath: str, file_size: int) -> dict:
        """파일명에서 스토리 정보를 추출합니다."""
        filename_parts = filename.replace('.json', '').split('_')
        
        # 새로운 형식: story_[name]_[type]_[timestamp].json
        if len(filename_parts) >= 4 and filename_parts[0] == 'story':
            story_name_parts = filename_parts[1:-2]  # 이름 부분 (여러 단어 가능)
            scenario_type = filename_parts[-2]  # 타입
            timestamp_part = filename_parts[-1]  # 타임스탬프
            
            story_name = ' '.join(story_name_parts).replace('_', ' ').title()
            
            return {
                "filename": filename,
                "filepath": filepath,
                "metadata": {
                    "story_name": story_name,
                    "scenario_type": scenario_type,
                    "created_at": self._extract_timestamp_from_filename(filename),
                    "user_requests": [],
                    "is_modified": True
                },
                "size": file_size
            }
        
        # 기존 형식: game_scenario_[type]_[timestamp].json
        elif len(filename_parts) >= 3 and filename_parts[0] == 'game' and filename_parts[1] == 'scenario':
            # 스토리 타입과 타임스탬프 분리
            scenario_type = '_'.join(filename_parts[2:-2]) if len(filename_parts) > 4 else filename_parts[2]
            
            # 스토리 이름을 파일명에서 추출하되 더 읽기 쉽게 변환
            story_name_mapping = {
                "magic_kingdom": "마법 왕국",
                "foodtruck_kingdom": "푸드트럭 왕국", 
                "moonlight_thief": "달빛 도둑",
                "three_little_pigs": "아기 돼지 삼형제"
            }
            
            display_name = story_name_mapping.get(scenario_type, scenario_type.replace('_', ' ').title())
            
            return {
                "filename": filename,
                "filepath": filepath,
                "metadata": {
                    "story_name": display_name,
                    "scenario_type": scenario_type,
                    "created_at": self._extract_timestamp_from_filename(filename),
                    "user_requests": [],
                    "is_modified": False
                },
                "size": file_size
            }
        
        # 기타 형식
        else:
            return {
                "filename": filename,
                "filepath": filepath,
                "metadata": {
                    "story_name": filename.replace('.json', '').replace('_', ' ').title(),
                    "scenario_type": "unknown",
                    "created_at": "",
                    "user_requests": [],
                    "is_modified": False
                },
                "size": file_size
            }

    def delete_story(self, filepath: str) -> bool:
        """저장된 스토리를 삭제합니다."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False
