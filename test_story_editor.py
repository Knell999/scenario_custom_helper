#!/usr/bin/env python3
"""
스토리 편집기 기능 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from source.components.story_editor import StoryEditor
from source.components.game_customizer import GameCustomizer

def test_story_editor():
    """스토리 편집기 기본 기능 테스트"""
    print("=== 스토리 편집기 테스트 시작 ===")
    
    # StoryEditor 초기화
    editor = StoryEditor()
    
    # 1. 사용 가능한 스토리 목록 테스트
    print("\n1. 사용 가능한 스토리 목록:")
    stories = editor.get_available_stories()
    print(f"발견된 스토리: {stories}")
    
    if not stories:
        print("저장된 스토리가 없습니다.")
        return
    
    # 2. 첫 번째 스토리 로드 테스트
    test_story = stories[0]
    print(f"\n2. '{test_story}' 스토리 로드 테스트:")
    story_data = editor.load_story(test_story)
    
    if story_data:
        print(f"스토리 로드 성공! 턴 수: {len(story_data) if isinstance(story_data, list) else 'Unknown'}")
        
        # 3. 스토리 요약 테스트
        print("\n3. 스토리 요약 생성:")
        summary = editor.get_story_summary(story_data)
        print(f"요약: {summary}")
        
        # 4. 구조 검증 테스트
        print("\n4. 스토리 구조 검증:")
        is_valid, errors = editor.validate_story_structure(story_data)
        print(f"유효성: {is_valid}")
        if errors:
            print(f"오류: {errors}")
        
        # 5. 수정 요청 분석 테스트
        print("\n5. 수정 요청 분석 테스트:")
        test_requests = [
            "빵집 캐릭터의 이름을 바꿔주세요",
            "3턴의 배경을 바꿔주세요",
            "전체적인 대화를 더 재미있게 만들어주세요"
        ]
        
        for request in test_requests:
            analysis = editor.analyze_modification_request(request)
            print(f"요청: '{request}' -> 분석: {analysis}")
    else:
        print("스토리 로드 실패")

def test_game_customizer():
    """게임 커스터마이저 통합 테스트"""
    print("\n=== 게임 커스터마이저 테스트 시작 ===")
    
    # GameCustomizer 초기화 (LLM 없이 테스트)
    customizer = GameCustomizer(llm=None)
    
    # 1. 사용 가능한 스토리 목록 테스트
    print("\n1. GameCustomizer를 통한 스토리 목록:")
    stories = customizer.get_available_stories()
    print(f"발견된 스토리: {stories}")
    
    if stories:
        # 2. 스토리 요약 테스트
        test_story = stories[0]
        print(f"\n2. '{test_story}' 스토리 요약:")
        summary = customizer.get_story_summary(test_story)
        print(f"요약: {summary}")

if __name__ == "__main__":
    try:
        test_story_editor()
        test_game_customizer()
        print("\n=== 모든 테스트 완료 ===")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
