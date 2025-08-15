interface ApiConfig {
  baseUrl: string;
  apiKey?: string;
  endpoints: {
    agent: string;
    chat: string;
    chatHistory: string;
    health: string;
  };
}

// Check if we're running in production (when served through APIM)
const isProduction = (import.meta as any).env?.PROD;

// APIM configuration
const apimConfig: ApiConfig = {
  baseUrl: window.location.origin,
  apiKey: (import.meta as any).env?.VITE_APIM_SUBSCRIPTION_KEY || '', // Optional: can be passed via headers
  endpoints: {
    agent: '/api/agent',
    chat: '/api/chat',
    chatHistory: '/api/chat/history',
    health: '/api/health'
  }
};

// Development configuration (direct to FastAPI)
const devConfig: ApiConfig = {
  baseUrl: (import.meta as any).env?.VITE_API_BASE_URL || window.location.origin,
  endpoints: {
    agent: '/agent',
    chat: '/chat',
    chatHistory: '/chat/history',
    health: '/health'
  }
};

export const apiConfig = isProduction ? apimConfig : devConfig;

export const makeApiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${apiConfig.baseUrl}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Add APIM subscription key if available
  if (apiConfig.apiKey) {
    headers['Ocp-Apim-Subscription-Key'] = apiConfig.apiKey;
  }

  const requestOptions: RequestInit = {
    ...options,
    headers,
    credentials: 'include',
  };

  try {
    const response = await fetch(url, requestOptions);
    
    if (!response.ok) {
      console.error(`API request failed: ${response.status} ${response.statusText}`);
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};
