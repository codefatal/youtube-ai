# 제목 텍스트 렌더링 수정 내역

**날짜**: 2025-12-30
**대상 파일**: `core/editor.py` (`_create_shorts_layout` 함수)
**요청 사항**: UPGRADE_AI.md - 제목 텍스트 하단 잘림 현상 해결

---

## 문제점

사용자가 생성된 영상에서 "제목 텍스트 하단이 잘리는 현상"을 보고함:
- 폰트의 Descender(g, j, y 등 아래로 내려가는 글자) 잘림
- 유튜브 쇼츠 UI(검색 버튼 등)에 제목이 가려짐
- stroke_width로 인한 글자 영역 확대 미고려

---

## 수정 내용

### 1. 수직 패딩 대폭 증가

**Before:**
```python
vertical_padding_ratio = 3.0 if line_count == 1 else 2.2
bg_height = int(text_height * (1 + vertical_padding_ratio))
interline=60
```

**After:**
```python
vertical_padding_ratio = 4.0 if line_count == 1 else 3.0
bg_height = int(text_height * (1 + vertical_padding_ratio)) + stroke_margin
interline=70
```

- 1줄 텍스트: 4.0배 (기존 3.0배)
- 2줄 이상: 3.0배 (기존 2.2배)
- 줄 간격(interline): 60px → 70px
- stroke_margin(6px) 추가 확보

---

### 2. 유튜브 쇼츠 Safe Zone 적용

**Before:**
```python
bg_y = max(20, (top_height - bg_height) // 2)  # 최소 20px 상단 여백
```

**After:**
```python
safe_zone_top = int(height * 0.07)  # 1920px * 0.07 = 약 134px
bg_y = safe_zone_top  # 상단 7% 지점부터 시작
```

- 유튜브 쇼츠 UI(검색 버튼, 프로필 등)에 가려지지 않도록
- 상단에서 약 7% (134px) 내려온 위치에 제목 배치
- 기존: 상단 20px 여백 → 수정: 상단 134px 여백

---

### 3. stroke_width 마진 추가

**Before:**
```python
bg_width = min(text_width + 80, width - 40)
```

**After:**
```python
stroke_width = 3
stroke_margin = stroke_width * 2  # 6px
bg_width = min(text_width + 80 + stroke_margin, width - 40)
```

- stroke_width(3px)로 인해 글자 영역이 확대됨
- stroke_margin(6px)을 좌우, 상하 패딩에 추가
- 외곽선이 잘리지 않도록 보장

---

### 4. Descender 버퍼 추가

**After:**
```python
descender_buffer = int(text_height * 0.15)  # 텍스트 높이의 15% 추가 버퍼
text_y = bg_y + (bg_height - text_height) // 2 - descender_buffer
text_y = max(bg_y + 10, text_y)  # 최소 10px 상단 여백 보장
```

- Descender(g, j, y 등) 잘림 방지
- 텍스트를 배경 박스 상단에 약간 붙여서 하단 여유 확보
- 텍스트 높이의 15%를 추가 버퍼로 확보

---

## 로그 출력 개선

**Before:**
```
[Title] 배경 박스 Y: 20px, 텍스트 Y: 50px, 상하 여유: 30px
```

**After:**
```
[Title] Safe Zone: 134px, 배경 Y: 134px, 텍스트 Y: 144px, 하단 여유: 50px
```

- Safe Zone 정보 추가
- 하단 여유 공간 명시 (Descender 잘림 방지 확인용)

---

## 기대 효과

1. **텍스트 잘림 방지**: Descender와 외곽선이 완전히 표시됨
2. **UI 회피**: 유튜브 쇼츠 UI 요소에 가려지지 않음
3. **가독성 향상**: 충분한 여백으로 제목이 더 깔끔하게 보임
4. **다국어 호환**: 한글, 영어 등 다양한 폰트의 Descender 지원

---

**작성자**: Claude Code
**커밋**: feat: 제목 텍스트 렌더링 개선 (Safe Zone, 패딩 증가)
