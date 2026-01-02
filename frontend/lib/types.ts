/**
 * Frontend Type Definitions
 * Phase 3: Draft & Timeline Editor Types
 */

// ============================================================
// Draft Status
// ============================================================

export type DraftStatus = 'editing' | 'assets_ready' | 'converting' | 'finalized';

// ============================================================
// Segment
// ============================================================

export interface Segment {
  segment_index: number;
  text: string;
  keyword: string | null;
  image_search_query: string | null;
  duration: number | null;

  // Assets
  video_url: string | null;
  video_local_path: string | null;
  video_provider: string | null;
  tts_local_path: string | null;
  tts_duration: number | null;
}

// ============================================================
// Draft Project
// ============================================================

export interface DraftProject {
  draft_id: string;
  topic: string;
  title: string;
  description: string | null;
  tags: string[];
  format: string;
  target_duration: number;
  status: DraftStatus;
  segments: Segment[];
  created_at: string;
  updated_at: string;
}

// ============================================================
// API Request/Response Types
// ============================================================

export interface CreateDraftRequest {
  topic?: string | null;
  format?: string;
  duration?: number;
  account_id?: number | null;
  style?: string;
  collect_assets?: boolean;
}

export interface CreateDraftResponse {
  draft_id: string;
  topic: string;
  title: string;
  description: string | null;
  tags: string[];
  format: string;
  target_duration: number;
  status: DraftStatus;
  segments: Segment[];
  created_at: string;
  updated_at: string;
}

export interface UpdateSegmentRequest {
  text?: string;
  keyword?: string;
  image_search_query?: string;
  duration?: number;
}

export interface UpdateSegmentResponse {
  success: boolean;
  data: Segment;
}

export interface FinalizeDraftRequest {
  upload?: boolean;
  template?: string | null;
  bgm_settings?: {
    enabled?: boolean;
    mood?: string;
    volume?: number;
  };
}

export interface FinalizeDraftResponse {
  success: boolean;
  data: {
    draft_id: string;
    job_id: string;
    status: string;
    output_video_path: string | null;
    youtube_url: string | null;
  };
}

// ============================================================
// Generic API Response
// ============================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  detail?: string;
}
