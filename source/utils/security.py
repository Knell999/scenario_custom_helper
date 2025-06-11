"""
보안 유틸리티 모듈
"""
import re
import hashlib
from typing import List, Dict, Any

class SecurityValidator:
    """보안 검증 클래스"""
    
    def __init__(self):
        # 금지된 내용 패턴
        self.banned_patterns = [
            r'api[_\-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]+',  # API 키 패턴
            r'password\s*[:=]\s*["\']?[a-zA-Z0-9]+',      # 패스워드
            r'secret\s*[:=]\s*["\']?[a-zA-Z0-9]+',        # 시크릿
            r'token\s*[:=]\s*["\']?[a-zA-Z0-9]+',         # 토큰
        ]
        
        # 부적절한 아동 콘텐츠
        self.inappropriate_words = [
            "폭력", "살인", "죽음", "혈액", "전쟁", "마약", "술", "담배",
            "성인", "섹스", "욕설", "비속어", "혐오", "차별", "괴롭히기"
        ]
    
    def validate_content_security(self, content: str) -> Dict[str, Any]:
        """콘텐츠 보안 검증"""
        result = {
            "is_safe": True,
            "issues": [],
            "severity": "low"
        }
        
        # API 키 등 민감 정보 검출
        for pattern in self.banned_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                result["is_safe"] = False
                result["issues"].append("민감한 정보가 포함되어 있습니다")
                result["severity"] = "high"
                break
        
        # 부적절한 아동 콘텐츠 검출
        content_lower = content.lower()
        found_inappropriate = []
        for word in self.inappropriate_words:
            if word in content_lower:
                found_inappropriate.append(word)
        
        if found_inappropriate:
            result["is_safe"] = False
            result["issues"].append(f"아동 부적절 내용: {', '.join(found_inappropriate)}")
            result["severity"] = "medium"
        
        return result
    
    def sanitize_input(self, user_input: str) -> str:
        """사용자 입력 정화"""
        # HTML 태그 제거
        sanitized = re.sub(r'<[^>]+>', '', user_input)
        
        # 스크립트 태그 제거
        sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # 길이 제한 (최대 1000자)
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000] + "..."
        
        return sanitized.strip()
    
    def validate_file_upload(self, filename: str, content: bytes) -> Dict[str, Any]:
        """파일 업로드 보안 검증"""
        result = {
            "is_safe": True,
            "issues": []
        }
        
        # 파일 확장자 검증
        allowed_extensions = ['.json', '.txt']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            result["is_safe"] = False
            result["issues"].append("허용되지 않은 파일 형식입니다")
        
        # 파일 크기 검증 (최대 5MB)
        if len(content) > 5 * 1024 * 1024:
            result["is_safe"] = False
            result["issues"].append("파일 크기가 너무 큽니다 (최대 5MB)")
        
        return result

# 전역 인스턴스
security_validator = SecurityValidator()
