const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface HealthResponse {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  service: string
  version?: string
  environment?: string
  services?: Record<string, string>
}

export interface APIInfo {
  name: string
  version: string
  description: string
  docs_url: string
  health_url: string
}

class ApiClient {
  private baseUrl: string
  private token?: string | null

  constructor(baseUrl: string = API_BASE_URL, token?: string | null) {
    this.baseUrl = baseUrl.replace(/\/$/, '') // Remove trailing slash
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    // Add authentication header if token is available
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const config: RequestInit = {
      headers,
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`

        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          // If we can't parse the error, use the default message
        }

        throw new Error(errorMessage)
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      } else {
        return response.text() as unknown as T
      }
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('An unexpected error occurred')
    }
  }

  async healthCheck(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/api/v1/health/')
  }

  async getRoot(): Promise<APIInfo> {
    return this.request<APIInfo>('/')
  }

  async getMetrics(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/api/v1/metrics/')
  }
}

// Default unauthenticated client (for public endpoints)
export const apiClient = new ApiClient()

// Factory function to create authenticated API client
export const createApiClient = (token?: string | null): ApiClient => {
  return new ApiClient(API_BASE_URL, token)
}
