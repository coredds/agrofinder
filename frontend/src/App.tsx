/**
 * Componente principal da aplicação AgroFinder
 */
import { useState, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { ResultsGrid } from './components/ResultsGrid';
import { UploadSection } from './components/UploadSection';
import { Login } from './components/Login';
import { api } from './services/api';
import { SearchResult, DocumentCategory } from './types';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [processingTime, setProcessingTime] = useState<number | undefined>();
  const [healthStatus, setHealthStatus] = useState<string>('checking');

  // Check if already authenticated on mount
  useEffect(() => {
    const auth = localStorage.getItem('agrofinder_auth');
    if (auth === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    localStorage.setItem('agrofinder_auth', 'true');
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('agrofinder_auth');
    setIsAuthenticated(false);
    setResults([]);
    setQuery('');
  };

  // Check health on mount - only if authenticated
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const checkHealth = async () => {
      try {
        const health = await api.health();
        setHealthStatus(health.status);
      } catch (err) {
        console.error('Health check failed:', err);
        setHealthStatus('unhealthy');
      }
    };
    checkHealth();
  }, [isAuthenticated]);

  const handleSearch = async (searchQuery: string, category?: DocumentCategory) => {
    setIsLoading(true);
    setError(null);
    setQuery(searchQuery);
    
    try {
      const response = await api.search({
        query: searchQuery,
        category,
        top_k: 10,
      });
      
      setResults(response.results);
      setProcessingTime(response.processing_time_ms);
    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.response?.data?.detail || 'Erro ao realizar busca. Tente novamente.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 via-green-50 to-gray-100 flex flex-col">
      {/* Header com tema verde agro - Responsivo */}
      <header className="bg-gradient-to-r from-primary-700 via-primary-600 to-primary-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center gap-2">
                🌾 AgroFinder
              </h1>
              <p className="text-xs sm:text-sm text-primary-100 mt-1">
                Busca semântica inteligente de documentos agro
              </p>
            </div>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-3 sm:px-4 py-2 rounded-full flex-1 sm:flex-none">
                <div className={`h-3 w-3 rounded-full ${
                  healthStatus === 'healthy' ? 'bg-green-400 animate-pulse' :
                  healthStatus === 'checking' ? 'bg-yellow-400 animate-pulse' :
                  'bg-red-400'
                }`}></div>
                <span className="text-xs sm:text-sm text-white font-medium">
                  {healthStatus === 'healthy' ? 'Sistema operacional' :
                   healthStatus === 'checking' ? 'Verificando...' :
                   'Sistema offline'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="bg-white/10 hover:bg-white/20 backdrop-blur-sm px-3 sm:px-4 py-2 rounded-full text-white text-xs sm:text-sm font-medium transition-all flex items-center gap-2"
                title="Sair"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="hidden sm:inline">Sair</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {/* Upload Section */}
        <UploadSection />

        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        <ResultsGrid
          results={results}
          isLoading={isLoading}
          query={query}
          processingTime={processingTime}
        />
      </main>

      {/* Footer minimalista */}
      <footer className="mt-auto bg-gradient-to-r from-primary-700 via-primary-600 to-primary-700 border-t border-primary-800">
        <div className="max-w-7xl mx-auto px-4 py-3 text-center">
          <p className="text-xs text-primary-100">
            AgroFinder v1.0 · Powered by OpenAI & Pinecone · Deployed on Google Cloud Run
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

