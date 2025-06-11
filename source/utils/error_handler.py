"""
에러 처리 및 알림 시스템
"""
import streamlit as st
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class NotificationType(Enum):
    """알림 타입"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

class ErrorHandler:
    """통합 에러 핸들러"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_history = []
        self.max_history = 50
    
    def handle_error(self, error: Exception, context: str = "", user_message: str = None):
        """에러 처리 및 로깅"""
        error_info = {
            "timestamp": datetime.now(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "user_message": user_message or "오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        }
        
        # 로깅
        self.logger.error(f"{context}: {error}", exc_info=True)
        
        # 히스토리 저장
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # 세션 상태 업데이트
        if 'error_count' not in st.session_state:
            st.session_state.error_count = 0
        st.session_state.error_count += 1
        st.session_state.last_error_time = datetime.now()
        
        # 사용자에게 표시
        st.error(error_info["user_message"])
        
        return error_info
    
    def show_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO):
        """사용자 알림 표시"""
        if notification_type == NotificationType.SUCCESS:
            st.success(message)
        elif notification_type == NotificationType.WARNING:
            st.warning(message)
        elif notification_type == NotificationType.ERROR:
            st.error(message)
        else:
            st.info(message)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """에러 통계"""
        if not self.error_history:
            return {"total_errors": 0, "recent_errors": 0, "common_errors": []}
        
        recent_errors = [e for e in self.error_history if (datetime.now() - e["timestamp"]).seconds < 3600]
        
        error_types = {}
        for error in self.error_history:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        common_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "common_errors": common_errors,
            "session_errors": st.session_state.get('error_count', 0)
        }
    
    def clear_error_history(self):
        """에러 히스토리 초기화"""
        self.error_history.clear()
        if 'error_count' in st.session_state:
            st.session_state.error_count = 0

class HealthChecker:
    """시스템 상태 체크"""
    
    def __init__(self):
        self.checks = {
            "api_key": self._check_api_key,
            "llm_model": self._check_llm_model,
            "story_files": self._check_story_files,
            "session_state": self._check_session_state
        }
    
    def _check_api_key(self) -> Dict[str, Any]:
        """API 키 상태 확인"""
        from source.utils.config import load_api_key
        try:
            api_key = load_api_key()
            return {
                "status": "healthy" if api_key else "unhealthy",
                "message": "API 키 로드됨" if api_key else "API 키 없음",
                "details": {"key_length": len(api_key) if api_key else 0}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"API 키 확인 실패: {str(e)}",
                "details": {}
            }
    
    def _check_llm_model(self) -> Dict[str, Any]:
        """LLM 모델 상태 확인"""
        try:
            if 'customizer' in st.session_state and st.session_state.customizer:
                return {
                    "status": "healthy",
                    "message": "LLM 모델 초기화됨",
                    "details": {"model_loaded": True}
                }
            else:
                return {
                    "status": "warning",
                    "message": "LLM 모델 미초기화",
                    "details": {"model_loaded": False}
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"LLM 모델 확인 실패: {str(e)}",
                "details": {}
            }
    
    def _check_story_files(self) -> Dict[str, Any]:
        """스토리 파일 상태 확인"""
        import os
        try:
            story_dir = "saved_stories"
            if not os.path.exists(story_dir):
                return {
                    "status": "error",
                    "message": "스토리 디렉토리 없음",
                    "details": {"directory_exists": False}
                }
            
            story_files = [f for f in os.listdir(story_dir) if f.endswith('.json')]
            return {
                "status": "healthy" if story_files else "warning",
                "message": f"{len(story_files)}개 스토리 파일 발견",
                "details": {"file_count": len(story_files), "files": story_files[:5]}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"스토리 파일 확인 실패: {str(e)}",
                "details": {}
            }
    
    def _check_session_state(self) -> Dict[str, Any]:
        """세션 상태 확인"""
        try:
            required_keys = ['chat_history', 'current_game_data', 'customizer']
            missing_keys = [key for key in required_keys if key not in st.session_state]
            
            return {
                "status": "healthy" if not missing_keys else "warning",
                "message": "세션 상태 정상" if not missing_keys else f"누락된 키: {missing_keys}",
                "details": {
                    "total_keys": len(st.session_state.keys()),
                    "missing_keys": missing_keys,
                    "error_count": st.session_state.get('error_count', 0)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"세션 상태 확인 실패: {str(e)}",
                "details": {}
            }
    
    def run_health_check(self) -> Dict[str, Any]:
        """전체 상태 체크 실행"""
        results = {}
        overall_status = "healthy"
        
        for check_name, check_func in self.checks.items():
            try:
                result = check_func()
                results[check_name] = result
                
                if result["status"] == "error":
                    overall_status = "error"
                elif result["status"] == "warning" and overall_status == "healthy":
                    overall_status = "warning"
                    
            except Exception as e:
                results[check_name] = {
                    "status": "error",
                    "message": f"체크 실행 실패: {str(e)}",
                    "details": {}
                }
                overall_status = "error"
        
        return {
            "overall_status": overall_status,
            "checks": results,
            "timestamp": datetime.now()
        }

# 전역 인스턴스
error_handler = ErrorHandler()
health_checker = HealthChecker()
