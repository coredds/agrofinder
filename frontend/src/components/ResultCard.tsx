/**
 * Componente de card de resultado com badges e detalhes
 */
import { SearchResult } from '../types';

interface ResultCardProps {
  result: SearchResult;
  index: number;
}

export const ResultCard = ({ result, index }: ResultCardProps) => {
  const getCategoryConfig = (category: string) => {
    const configs = {
      anuncio: {
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        icon: '📢',
        label: 'Anúncio'
      },
      organico: {
        color: 'bg-green-100 text-green-800 border-green-200',
        icon: '🌱',
        label: 'Orgânico'
      },
      relatorio: {
        color: 'bg-purple-100 text-purple-800 border-purple-200',
        icon: '📊',
        label: 'Relatório'
      }
    };
    return configs[category as keyof typeof configs] || configs.relatorio;
  };

  const getRelevanceConfig = (score: number) => {
    const percentage = score * 100;
    if (percentage >= 70) return { color: 'bg-green-500', label: 'Alta', textColor: 'text-green-700' };
    if (percentage >= 50) return { color: 'bg-yellow-500', label: 'Média', textColor: 'text-yellow-700' };
    return { color: 'bg-gray-500', label: 'Baixa', textColor: 'text-gray-700' };
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('pt-BR', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  };

  const truncateText = (text: string, maxLength: number = 300) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const categoryConfig = getCategoryConfig(result.category);
  const relevanceConfig = getRelevanceConfig(result.similarity_score);
  const wordCount = result.chunk_text.split(/\s+/).length;

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-4 sm:p-6 border border-gray-200 hover:border-primary-300">
      {/* Header com ranking - Responsivo */}
      <div className="flex items-start gap-3 sm:gap-4 mb-4">
        {/* Ranking Badge - Responsivo */}
        <div className="flex-shrink-0">
          <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center font-bold text-lg sm:text-xl
            ${index === 0 ? 'bg-yellow-100 text-yellow-700 border-2 border-yellow-300' : 
              index === 1 ? 'bg-gray-100 text-gray-600 border-2 border-gray-300' : 
              index === 2 ? 'bg-orange-100 text-orange-600 border-2 border-orange-300' : 
              'bg-gray-50 text-gray-500 border border-gray-200'}`}>
            #{index + 1}
          </div>
        </div>

        {/* Título e Badges - Responsivo */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm sm:text-lg text-gray-900 mb-2 line-clamp-2 sm:truncate" title={result.filename}>
            {result.filename}
          </h3>
          
          {/* Badges Row - Responsivo */}
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
            {/* Categoria Badge */}
            <span className={`inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full font-medium border ${categoryConfig.color}`}>
              <span>{categoryConfig.icon}</span>
              {categoryConfig.label}
            </span>

            {/* Relevância Badge */}
            <span className={`inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full font-semibold bg-white border-2 ${relevanceConfig.textColor}`}
                  style={{ borderColor: 'currentColor' }}>
              <div className={`w-2 h-2 rounded-full ${relevanceConfig.color}`}></div>
              {(result.similarity_score * 100).toFixed(0)}% relevante
            </span>

            {/* Página Badge */}
            {result.page_number && (
              <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                Pág. {result.page_number}
              </span>
            )}

            {/* Data Badge */}
            <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600 border border-gray-200">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {formatDate(result.upload_date)}
            </span>

            {/* Tamanho do texto Badge */}
            <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {wordCount} palavras
            </span>
          </div>
        </div>
      </div>

      {/* Preview do Conteúdo - Responsivo */}
      <div className="mt-3 sm:mt-4 mb-3 sm:mb-4">
        <div className="bg-gray-50 rounded-lg p-3 sm:p-4 border border-gray-200">
          <p className="text-gray-700 text-xs sm:text-sm leading-relaxed">
            {truncateText(result.chunk_text, window.innerWidth < 640 ? 200 : 300)}
          </p>
        </div>
      </div>

      {/* Footer com Ações - Responsivo */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-4 border-t border-gray-100">
        {/* Document ID (oculto em mobile) */}
        <div className="hidden md:flex items-center gap-2 text-xs text-gray-400">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
          <span className="font-mono truncate max-w-xs" title={result.document_id}>
            ID: {result.document_id.substring(0, 8)}...
          </span>
        </div>

        {/* Botão Ver PDF - Responsivo */}
        <a
          href={result.gcs_url}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 sm:px-5 py-2 sm:py-2.5 text-xs sm:text-sm text-white bg-primary-600 hover:bg-primary-700 rounded-lg font-medium transition-all duration-200 hover:shadow-lg hover:scale-105"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          Ver Documento
        </a>
      </div>
    </div>
  );
};

