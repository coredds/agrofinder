/**
 * Tipos TypeScript para AgroFinder
 */

export enum DocumentCategory {
  ANUNCIO = "anuncio",
  ORGANICO = "organico"
}

export interface SearchRequest {
  query: string;
  category?: DocumentCategory;
  top_k?: number;
  date_from?: string;
  date_to?: string;
}

export interface SearchResult {
  document_id: string;
  filename: string;
  category: DocumentCategory;
  chunk_text: string;
  similarity_score: number;
  upload_date: string;
  page_number?: number;
  gcs_url: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
  processing_time_ms: number;
}

export interface HealthResponse {
  status: string;
  environment: string;
  vector_db: string;
  total_vectors: number;
  timestamp: string;
}

