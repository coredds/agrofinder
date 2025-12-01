/**
 * API Service - Cliente para comunicação com backend
 */
import axios from 'axios';
import { SearchRequest, SearchResponse, HealthResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 segundos
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * Busca semântica
   */
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>('/search', request);
    return response.data;
  },

  /**
   * Health check
   */
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  /**
   * Upload de PDF
   */
  uploadPDF: async (file: File, category: string): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Ingestão manual
   */
  ingest: async (gcsPath: string, category: string): Promise<any> => {
    const response = await apiClient.post('/ingest', {
      gcs_path: gcsPath,
      category,
    });
    return response.data;
  },
};

