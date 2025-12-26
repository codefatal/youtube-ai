# tests/test_tts_caching.py
import time
from core.asset_manager import AssetManager

asset_manager = AssetManager(tts_provider="elevenlabs")

text = "이것은 캐싱 테스트입니다."

# 첫 번째 호출 (API 호출)
start = time.time()
filepath1 = asset_manager._generate_elevenlabs(text)
time1 = time.time() - start

# 두 번째 호출 (캐시)
start = time.time()
filepath2 = asset_manager._generate_elevenlabs(text)
time2 = time.time() - start

# 캐싱으로 인한 속도 향상 확인
assert filepath1 == filepath2
assert time2 < time1 * 0.1  # 10배 이상 빠름
print(f"첫 호출: {time1:.2f}초, 캐시 호출: {time2:.4f}초")
print(f"속도 향상: {time1/time2:.1f}배")