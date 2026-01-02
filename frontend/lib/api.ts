/**
 * API Client Functions
 * Phase 3: Draft & Timeline Editor API
 */

import type {
  CreateDraftRequest,
  CreateDraftResponse,
  DraftProject,
  UpdateSegmentRequest,
  UpdateSegmentResponse,
  FinalizeDraftRequest,
  FinalizeDraftResponse,
  ApiResponse,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================
// Draft API
// ============================================================

/**
 * Create a new draft (script + assets, no rendering)
 */
export async function createDraft(
  request: CreateDraftRequest
): Promise<CreateDraftResponse> {
  const response = await fetch(`${API_URL}/api/draft/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to create draft: ${response.statusText}`);
  }

  const data: CreateDraftResponse = await response.json();
  return data;
}

/**
 * Get draft project detail (with segments)
 */
export async function getProjectDetail(draftId: string): Promise<DraftProject> {
  const response = await fetch(`${API_URL}/api/draft/${draftId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to get project: ${response.statusText}`);
  }

  const data: DraftProject = await response.json();
  return data;
}

/**
 * Update a specific segment
 */
export async function updateSegment(
  draftId: string,
  segmentIndex: number,
  request: UpdateSegmentRequest
): Promise<UpdateSegmentResponse> {
  const response = await fetch(
    `${API_URL}/api/draft/${draftId}/update-segment/${segmentIndex}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to update segment: ${response.statusText}`);
  }

  const data: UpdateSegmentResponse = await response.json();
  return data;
}

/**
 * Regenerate video asset for a specific segment
 * (re-fetch video using image_search_query or keyword)
 */
export async function regenerateSegmentVideo(
  draftId: string,
  segmentIndex: number
): Promise<UpdateSegmentResponse> {
  // 현재 세그먼트 정보 조회
  const project = await getProjectDetail(draftId);
  const segment = project.segments.find(
    (seg) => seg.segment_index === segmentIndex
  );

  if (!segment) {
    throw new Error(`Segment ${segmentIndex} not found`);
  }

  // image_search_query 또는 keyword를 사용하여 재검색
  // NOTE: 실제로는 백엔드에 별도 API가 필요하지만,
  // 현재는 segment.image_search_query를 동일하게 유지하면서
  // 캐시를 무시하고 재검색하도록 요청

  // 임시 구현: 동일한 값으로 업데이트 (백엔드에서 재검색 로직 필요)
  return await updateSegment(draftId, segmentIndex, {
    image_search_query: segment.image_search_query || segment.keyword || '',
  });
}

/**
 * Finalize draft and render final video
 */
export async function finalizeDraft(
  draftId: string,
  request: FinalizeDraftRequest
): Promise<FinalizeDraftResponse> {
  const response = await fetch(`${API_URL}/api/draft/${draftId}/finalize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to finalize draft: ${response.statusText}`);
  }

  const data: FinalizeDraftResponse = await response.json();
  return data;
}

/**
 * List all drafts
 */
export async function listDrafts(
  skip: number = 0,
  limit: number = 20,
  accountId?: number,
  status?: string
): Promise<DraftProject[]> {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });

  if (accountId !== undefined) {
    params.append('account_id', accountId.toString());
  }
  if (status) {
    params.append('status', status);
  }

  const response = await fetch(`${API_URL}/api/draft/?${params.toString()}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to list drafts: ${response.statusText}`);
  }

  const data: DraftProject[] = await response.json();
  return data;
}

/**
 * Delete a draft
 */
export async function deleteDraft(draftId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/draft/${draftId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete draft: ${response.statusText}`);
  }
}

// ============================================================
// Helper Functions
// ============================================================

/**
 * Get TTS audio URL for playback
 */
export function getTTSAudioUrl(ttsLocalPath: string | null): string | null {
  if (!ttsLocalPath) return null;

  // Windows 경로 구분자를 URL 슬래시로 변환
  const normalizedPath = ttsLocalPath.replace(/\\/g, '/');

  // TTS 파일 경로를 절대 URL로 변환
  // 예: downloads/audio/tts_xxxxx.mp3 → http://localhost:8000/downloads/audio/tts_xxxxx.mp3
  return `${API_URL}/${normalizedPath}`;
}

/**
 * Get video thumbnail URL
 */
export function getVideoThumbnailUrl(videoUrl: string | null): string | null {
  if (!videoUrl) return null;

  // Pexels/Pixabay URL을 그대로 사용
  if (videoUrl.startsWith('http')) {
    return videoUrl;
  }

  // Windows 경로 구분자를 URL 슬래시로 변환
  const normalizedPath = videoUrl.replace(/\\/g, '/');

  // 로컬 경로라면 절대 URL로 변환
  return `${API_URL}/${normalizedPath}`;
}
