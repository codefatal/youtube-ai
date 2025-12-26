# tests/test_tts_advanced.py
from core.asset_manager import AssetManager

asset_manager = AssetManager(tts_provider="elevenlabs")

# 안정성 낮음 (감정 풍부)
filepath1 = asset_manager._generate_elevenlabs(
    text="안녕하세요! 오늘은 정말 신나는 하루입니다!",
    stability=0.3,
    similarity_boost=0.75,
    style=0.5
)

# 안정성 높음 (일관성)
filepath2 = asset_manager._generate_elevenlabs(
    text="안녕하세요! 오늘은 정말 신나는 하루입니다!",
    stability=0.9,
    similarity_boost=0.75,
    style=0.0
)

# 두 파일이 다르게 생성되었는지 확인
assert filepath1 != filepath2
print("파라미터별 음성 생성 성공")