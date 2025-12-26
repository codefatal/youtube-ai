# YouTube AI v4.0 개선 작업 목록

**작성일**: 2025-12-26
**상태**: 진행 예정

---

## 📋 전체 개선사항 요약

1. ✅ 자막 시스템 개선 (크기, 가독성)
2. ✅ 제목 및 자막 레이아웃 개선 (잘림 방지)
3. ✅ 영상 레이아웃 통일 (상단/하단 검은 바탕)
4. ✅ 영상 길이 정확도 개선
5. ✅ TTS Voice ID 옵션 확대
6. ✅ BGM 자동/수동 추가 기능
7. ✅ 작업 이력 UI/UX 개선
8. ✅ 작업 이력 페이징 처리
9. ✅ 스케줄링/설정 페이지 완성

---

## Phase 1: 자막 시스템 개선 (Issue #1, #2)

### 문제점
- 기본형, 다큐형, 예능형 모든 템플릿에서 자막 크기가 너무 작음
- 자막이 제대로 표기되지 않음
- TTS와 자막이 동기화되지 않음
- 자막이 중간에 잘리는 현상 발생

### 목표
- 쇼츠에 적합한 자막 크기 (폰트 크기 60-80)
- TTS 음성과 완벽한 동기화
- 자막 단어 단위 줄바꿈으로 잘림 방지
- 가독성 높은 자막 스타일 (외곽선, 그림자)

### 참고 영상
- https://www.youtube.com/shorts/75ZpzLHI2Ps
- https://www.youtube.com/shorts/vCVsDgLmnnk
- https://www.youtube.com/shorts/TxWHrbzxDus

### 작업 내용

#### Backend
1. **`core/editor.py` 수정**
   - `_create_subtitle_clip()` 메서드 개선
   - 폰트 크기: 60-80으로 증가
   - 텍스트 외곽선 (stroke) 추가: 검은색 2-3px
   - 그림자 효과 추가
   - 최대 줄 길이 제한 (15-20자)
   - 단어 단위 줄바꿈 로직 추가

2. **`templates/*.json` 업데이트**
   - `subtitle.fontsize`: 70
   - `subtitle.stroke_color`: "black"
   - `subtitle.stroke_width`: 3
   - `subtitle.position`: ("center", "center")

#### Frontend
- 변경 없음 (백엔드에서 처리)

#### 테스트 체크리스트
- [ ] 자막 크기가 충분히 큼 (모바일에서 확인)
- [ ] TTS와 자막 타이밍 일치
- [ ] 긴 문장도 잘리지 않음
- [ ] 3가지 템플릿 모두 적용 확인

---

## Phase 2: 영상 레이아웃 통일 (Issue #3)

### 문제점
- 영상이 전체 화면을 차지함
- 제목이 별도로 표시되지 않음
- 유튜브 쇼츠 표준 레이아웃과 다름

### 목표
- **상단 1/4 (480px)**: 검은 바탕 + 제목
- **중앙 1/2 (960px)**: 실제 영상 콘텐츠
- **하단 1/4 (480px)**: 검은 바탕
- 해상도: 1080x1920 (쇼츠)

### 참고 영상
- https://www.youtube.com/shorts/TbB05zKzizI
- https://www.youtube.com/shorts/13eYgAGgBVs

### 작업 내용

#### Backend
1. **`core/editor.py` 수정**
   - `create_video()` 메서드 리팩토링
   - 검은 바탕 클립 생성 (1080x480, ColorClip)
   - 제목 텍스트 클립 생성 (상단, 폰트 크기 80-100)
   - 영상 클립 리사이즈 (1080x960)
   - CompositeVideoClip으로 합성:
     ```
     [상단 검은바탕 + 제목]
     [중앙 영상]
     [하단 검은바탕]
     ```

2. **`core/models.py`**
   - `TemplateConfig`에 `layout` 필드 추가:
     - `title_height`: 480
     - `video_height`: 960
     - `footer_height`: 480

#### Frontend
- 변경 없음 (백엔드에서 처리)

#### 테스트 체크리스트
- [ ] 상단 검은 바탕 + 제목 표시
- [ ] 중앙 영상 영역만 콘텐츠 표시
- [ ] 하단 검은 바탕 표시
- [ ] 전체 해상도 1080x1920 유지

---

## Phase 3: 영상 길이 정확도 개선 (Issue #4)

### 문제점
- 목표 길이를 60초로 설정해도 실제 생성 길이가 다름
- 세그먼트 시간 계산이 부정확함

### 목표
- 목표 길이 ±1초 이내 정확도
- TTS 길이 기반 정확한 시간 계산

### 작업 내용

#### Backend
1. **`core/planner.py` 수정**
   - `_validate_and_adjust_duration()` 메서드 강화
   - TTS 예상 길이 계산 개선 (글자 수 * 0.15초)
   - 세그먼트별 시간 재조정 로직 추가
   - 최종 검증: `±1초` 이내 강제

2. **`core/asset_manager.py` 수정**
   - 실제 TTS 파일 길이 측정 (pydub)
   - 길이 정보 AssetBundle에 포함

3. **`core/editor.py` 수정**
   - 영상 클립 길이를 TTS 길이에 정확히 맞춤
   - 남는 시간은 마지막 클립 반복

#### Frontend
- 변경 없음 (백엔드에서 처리)

#### 테스트 체크리스트
- [ ] 60초 설정 → 59-61초 생성
- [ ] 90초 설정 → 89-91초 생성
- [ ] 30초 설정 → 29-31초 생성

---

## Phase 4: TTS Voice ID 옵션 확대 (Issue #5)

### 문제점
- Voice ID 선택지가 너무 적음
- 현재 기본 1개만 제공

### 목표
- ElevenLabs Voice 10개 이상 제공
- 한국어 지원 Voice 우선

### 작업 내용

#### Backend
1. **`backend/routers/tts.py` 수정**
   - `/api/tts/voices` 엔드포인트 개선
   - ElevenLabs API에서 실시간 Voice 목록 가져오기
   - 한국어 지원 Voice 필터링

2. **Voice 목록 하드코딩 (Fallback)**
   ```python
   ELEVENLABS_VOICES = [
       {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam (남성)", "language": "en"},
       {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel (여성)", "language": "en"},
       {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi (여성)", "language": "en"},
       {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella (여성)", "language": "en"},
       {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni (남성)", "language": "en"},
       {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli (여성)", "language": "en"},
       {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh (남성)", "language": "en"},
       {"id": "VR6AewLTigWG4xSOukaG", "name": "Arnold (남성)", "language": "en"},
       {"id": "pqHfZKP75CvOlQylNhV4", "name": "Bill (남성)", "language": "en"},
       {"id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam (남성)", "language": "en"},
   ]
   ```

#### Frontend
1. **`frontend/app/create/page.tsx` 수정**
   - Voice ID 드롭다운 추가
   - `/api/tts/voices` API 호출
   - 음성 이름과 언어 표시

2. **UI 개선**
   - Voice 미리듣기 버튼 추가 (선택 사항)
   - 드롭다운에서 음성 설명 표시

#### 테스트 체크리스트
- [ ] Voice 목록 API 정상 작동
- [ ] 프론트엔드 드롭다운에 10개 이상 표시
- [ ] 선택한 Voice로 TTS 생성 확인

---

## Phase 5: BGM 자동/수동 추가 기능 (Issue #6)

### 문제점
- BGM이 자동으로 추가되지 않음
- 수동으로 BGM을 추가하는 UI가 없음

### 목표
- 자동 BGM 선택 및 적용
- 수동 BGM 업로드/선택 기능

### 작업 내용

#### Backend
1. **BGM 자동 선택 활성화**
   - `core/orchestrator.py`: `bgm_enabled=True` 기본값
   - `core/asset_manager.py`: 주제/톤 기반 BGM 자동 선택
   - `core/bgm_manager.py`: `auto_select_mood()` 활용

2. **BGM API 엔드포인트 추가**
   - `GET /api/bgm/list` - 사용 가능한 BGM 목록
   - `POST /api/bgm/upload` - BGM 파일 업로드
   - `GET /api/bgm/moods` - 분위기별 BGM 목록

3. **BGM 설정 모델 추가**
   ```python
   class BGMSettings(BaseModel):
       enabled: bool = True
       mood: Optional[str] = None  # auto, happy, sad, energetic...
       volume: float = 0.3
       custom_file: Optional[str] = None
   ```

#### Frontend
1. **`frontend/app/create/page.tsx` 수정**
   - BGM 설정 섹션 추가
   - BGM 활성화 체크박스
   - 분위기 선택 라디오 버튼 (자동, 행복, 슬픔, 활기찬...)
   - BGM 볼륨 슬라이더 (0.0 - 1.0)
   - 커스텀 BGM 파일 업로드

2. **UI 레이아웃**
   ```tsx
   <div className="bgm-settings">
     <h3>배경음악 (BGM)</h3>
     <label>
       <input type="checkbox" checked={bgmEnabled} />
       BGM 사용
     </label>

     <select value={bgmMood}>
       <option value="auto">자동 선택</option>
       <option value="happy">행복한</option>
       <option value="energetic">활기찬</option>
       <option value="calm">차분한</option>
     </select>

     <input type="range" min="0" max="1" step="0.1" value={bgmVolume} />

     <input type="file" accept="audio/*" />
   </div>
   ```

#### 테스트 체크리스트
- [ ] BGM 자동 선택 작동
- [ ] 프론트엔드에서 BGM 설정 가능
- [ ] 커스텀 BGM 업로드 및 적용
- [ ] BGM 볼륨 조절 작동

---

## Phase 6: 작업 이력 UI/UX 개선 (Issue #7, #8)

### 문제점
- 상세보기 클릭 시 하단에 정보 표시
- 정보가 제대로 표기되지 않음
- 페이징 처리 없어 많은 작업 시 느림

### 목표
- 상세보기 클릭 시 작업 목록 바로 아래 표시 (아코디언)
- 모든 정보 정확히 표기
- 페이징 처리 (10개씩)

### 작업 내용

#### Backend
1. **`backend/main.py` 수정**
   - `/api/jobs/recent` 페이징 파라미터 추가
   ```python
   @app.get("/api/jobs/recent")
   async def get_recent_jobs(page: int = 1, limit: int = 10):
       offset = (page - 1) * limit
       jobs = db.query(DBJobHistory).order_by(...).offset(offset).limit(limit).all()
       total = db.query(func.count(DBJobHistory.id)).scalar()
       return {
           "jobs": [...],
           "total": total,
           "page": page,
           "total_pages": (total + limit - 1) // limit
       }
   ```

2. **상세 정보 API 개선**
   - `/api/jobs/status` 응답에 모든 필드 포함
   - 스크립트 세그먼트 정보 포함 (선택 사항)

#### Frontend
1. **`frontend/app/jobs/page.tsx` 완전 리팩토링**
   - 아코디언 UI로 변경 (클릭 시 바로 아래 펼침)
   - 페이징 컴포넌트 추가
   - 상세 정보 표시 개선

2. **UI 구조**
   ```tsx
   <div className="job-list">
     {jobs.map(job => (
       <div key={job.job_id} className="job-item">
         <div className="job-header" onClick={() => toggleDetail(job.job_id)}>
           <span>{job.topic}</span>
           <span>{job.status}</span>
         </div>

         {expandedJob === job.job_id && (
           <div className="job-detail">
             <p>Job ID: {job.job_id}</p>
             <p>포맷: {job.format}</p>
             <p>생성 시각: {job.created_at}</p>
             <p>완료 시각: {job.completed_at}</p>
             <p>영상 경로: {job.output_video_path}</p>
             <p>YouTube URL: {job.youtube_url}</p>
             {job.error_log && <p>에러: {job.error_log}</p>}
           </div>
         )}
       </div>
     ))}

     <Pagination
       currentPage={page}
       totalPages={totalPages}
       onPageChange={setPage}
     />
   </div>
   ```

#### 테스트 체크리스트
- [ ] 상세보기 클릭 시 바로 아래 펼쳐짐
- [ ] 모든 정보 정확히 표시
- [ ] 페이징 작동 (다음/이전 페이지)
- [ ] 50개 이상 작업 시 성능 확인

---

## Phase 7: 스케줄링/설정 페이지 완성 (Issue #9)

### 문제점
- 스케줄링 메뉴가 없음
- 설정 페이지가 제대로 만들어지지 않음
- 계정별 설정 불가능

### 목표
- 스케줄링 관리 페이지 완성
- 설정 페이지 완성
- 계정별 설정 가능

### 작업 내용

#### Backend
1. **스케줄러 API 완성** (`backend/routers/scheduler.py`)
   - `GET /api/scheduler/jobs` - 등록된 스케줄 목록
   - `POST /api/scheduler/create` - 스케줄 생성
   - `PUT /api/scheduler/update/{job_id}` - 스케줄 수정
   - `DELETE /api/scheduler/delete/{job_id}` - 스케줄 삭제
   - `POST /api/scheduler/trigger/{account_id}` - 즉시 실행

2. **설정 API 추가**
   - `GET /api/settings` - 전체 설정 조회
   - `PUT /api/settings` - 설정 업데이트
   - 설정 항목:
     - AI Provider (Gemini, Claude)
     - TTS Provider (gTTS, ElevenLabs)
     - 기본 영상 포맷
     - 기본 영상 길이
     - BGM 기본 설정

#### Frontend
1. **`frontend/app/automation/page.tsx` 완성**
   - 스케줄 목록 표시
   - 스케줄 생성 폼
   - Cron 표현식 입력 (또는 시각화된 UI)
   - 계정 선택 드롭다운
   - 즉시 실행 버튼

2. **`frontend/app/settings/page.tsx` 완성**
   - AI 설정 섹션
   - TTS 설정 섹션
   - 영상 기본 설정 섹션
   - BGM 기본 설정 섹션
   - 저장 버튼

3. **Sidebar 메뉴 추가**
   - "자동화" (Automation) - `/automation`
   - "설정" (Settings) - `/settings`

#### 테스트 체크리스트
- [ ] 스케줄 생성/수정/삭제 작동
- [ ] Cron 표현식 검증
- [ ] 설정 저장 및 불러오기 작동
- [ ] 계정별 스케줄 구분

---

## 🚀 작업 우선순위

### 높음 (High Priority)
- **Phase 1**: 자막 시스템 개선 ⭐⭐⭐
- **Phase 2**: 영상 레이아웃 통일 ⭐⭐⭐
- **Phase 3**: 영상 길이 정확도 개선 ⭐⭐⭐

### 중간 (Medium Priority)
- **Phase 5**: BGM 자동/수동 추가 기능 ⭐⭐
- **Phase 6**: 작업 이력 UI/UX 개선 ⭐⭐

### 낮음 (Low Priority)
- **Phase 4**: TTS Voice ID 옵션 확대 ⭐
- **Phase 7**: 스케줄링/설정 페이지 완성 ⭐

---

## 📝 작업 진행 방법

### 각 Phase 시작 시
1. 해당 Phase 섹션 읽기
2. Backend 작업 먼저 완료
3. Frontend 작업 완료
4. 테스트 체크리스트 확인
5. Git commit & push
6. 다음 Phase로 이동

### 커밋 메시지 형식
```
Phase {N}: {Phase 제목}

- 백엔드: {변경사항}
- 프론트엔드: {변경사항}
- 테스트: {테스트 결과}
```

### 예시
```
Phase 1: 자막 시스템 개선

- 백엔드: editor.py 자막 크기 60→80, 외곽선 추가
- 프론트엔드: 변경 없음
- 테스트: 3가지 템플릿 모두 자막 크기 확인 완료
```

---

## ✅ 완료 기준

각 Phase는 다음 조건을 모두 만족해야 완료:
1. Backend 코드 구현 완료
2. Frontend 코드 구현 완료 (필요 시)
3. 테스트 체크리스트 모두 통과
4. Git commit & push 완료
5. 실제 영상 생성 테스트 성공

---

**작업 시작**: Phase 1부터 순차적으로 진행
**예상 소요 시간**: 각 Phase당 30분-1시간
**총 예상 시간**: 4-7시간
