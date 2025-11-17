/**
 * Frontend configuration
 *
 * This file centralizes all environment variable access and provides
 * type-safe configuration for the frontend application.
 */

export const config = {
  /**
   * Backend API URL
   * Falls back to localhost for development
   */
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

  /**
   * Enable localStorage fallback
   * Disabled by default in production for security
   */
  useLocalStorage: process.env.NEXT_PUBLIC_USE_LOCALSTORAGE === 'true',

  /**
   * API request timeout in milliseconds
   */
  apiTimeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000', 10),
} as const

/**
 * Validate configuration on load
 */
export function validateConfig(): void {
  if (!config.apiUrl) {
    throw new Error('NEXT_PUBLIC_API_URL is required')
  }

  if (!config.apiUrl.startsWith('http://') && !config.apiUrl.startsWith('https://')) {
    throw new Error('NEXT_PUBLIC_API_URL must start with http:// or https://')
  }
}

// Validate on module load (only in browser)
if (typeof window !== 'undefined') {
  validateConfig()
}
