const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  }

  async get(endpoint: string, options?: RequestInit) {
    const response = await this.request(endpoint, { ...options, method: 'GET' });
    return response.json();
  }

  async post(endpoint: string, data?: any, options?: RequestInit) {
    const response = await this.request(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
    return response.json();
  }

  async put(endpoint: string, data?: any, options?: RequestInit) {
    const response = await this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
    return response.json();
  }

  async delete(endpoint: string, options?: RequestInit) {
    const response = await this.request(endpoint, { ...options, method: 'DELETE' });
    return response.json();
  }

  async postStream(endpoint: string, data?: any, options?: RequestInit) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async postFormData(endpoint: string, formData: FormData, options?: RequestInit) {
    const config: RequestInit = {
      ...options,
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData, let browser set it
        ...options?.headers,
      },
    };
    // Remove Content-Type header to let browser set boundary for FormData
    const headers = { ...config.headers };
    delete (headers as any)['Content-Type'];
    config.headers = headers;

    const response = await this.request(endpoint, config);
    return response.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);