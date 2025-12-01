/**
 * Componente de grid de resultados
 */
import { SearchResult } from '../types';
import { ResultCard } from './ResultCard';

interface ResultsGridProps {
  results: SearchResult[];
  isLoading: boolean;
  query: string;
  processingTime?: number;
}

export const ResultsGrid = ({ results, isLoading, query, processingTime }: ResultsGridProps) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 sm:py-20">
        <div className="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-b-2 border-primary-600"></div>
        <p className="mt-4 text-gray-600 text-sm sm:text-base">Buscando documentos relevantes...</p>
      </div>
    );
  }

  if (!query) {
    return (
      <div className="text-center py-12 sm:py-20 px-4">
        <svg className="mx-auto h-16 w-16 sm:h-24 sm:w-24 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <h3 className="mt-4 text-lg sm:text-xl font-medium text-gray-900">Busca Semântica de Documentos</h3>
        <p className="mt-2 text-sm sm:text-base text-gray-500 max-w-md mx-auto">
          Digite uma busca acima para encontrar documentos relevantes usando inteligência artificial.
        </p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-12 sm:py-20 px-4">
        <svg className="mx-auto h-16 w-16 sm:h-24 sm:w-24 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="mt-4 text-lg sm:text-xl font-medium text-gray-900">Nenhum resultado encontrado</h3>
        <p className="mt-2 text-sm sm:text-base text-gray-500 max-w-md mx-auto">
          Tente reformular sua busca ou usar outros termos.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Header dos resultados - Responsivo */}
      <div className="mb-4 sm:mb-6 pb-3 sm:pb-4 border-b border-gray-200">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
          {results.length} {results.length === 1 ? 'resultado encontrado' : 'resultados encontrados'}
        </h2>
        {processingTime && (
          <p className="text-xs sm:text-sm text-gray-500 mt-1">
            Busca processada em {processingTime.toFixed(0)}ms
          </p>
        )}
      </div>

      {/* Grid de resultados - Responsivo */}
      <div className="space-y-3 sm:space-y-4">
        {results.map((result, index) => (
          <ResultCard key={result.document_id + index} result={result} index={index} />
        ))}
      </div>
    </div>
  );
};

