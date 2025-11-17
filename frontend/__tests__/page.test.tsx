import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import HomePage from '@/app/page'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

describe('HomePage', () => {
  let mockPush: jest.Mock
  let mockFetch: jest.Mock

  beforeEach(() => {
    mockPush = jest.fn()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })

    mockFetch = jest.fn()
    global.fetch = mockFetch

    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders the hero section', () => {
    render(<HomePage />)

    expect(screen.getByText('AI-Powered Brand Intelligence')).toBeInTheDocument()
    expect(
      screen.getByText(/Analyze prompts and get instant insights/i)
    ).toBeInTheDocument()
  })

  it('renders the input section', () => {
    render(<HomePage />)

    expect(screen.getByPlaceholderText(/Enter your prompt here/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Analyze/i })).toBeInTheDocument()
  })

  it('renders analysis tiles preview', () => {
    render(<HomePage />)

    expect(screen.getByText('Sentiment Analysis')).toBeInTheDocument()
    expect(screen.getByText('Brand Mention Tracking')).toBeInTheDocument()
    expect(screen.getByText('Website Coverage')).toBeInTheDocument()
    expect(screen.getByText('Trust/Authority Score')).toBeInTheDocument()
  })

  it('disables analyze button when prompt is empty', () => {
    render(<HomePage />)

    const analyzeButton = screen.getByRole('button', { name: /Analyze/i })
    expect(analyzeButton).toBeDisabled()
  })

  it('enables analyze button when prompt has content', () => {
    render(<HomePage />)

    const textarea = screen.getByPlaceholderText(/Enter your prompt here/i)
    const analyzeButton = screen.getByRole('button', { name: /Analyze/i })

    fireEvent.change(textarea, { target: { value: 'Test prompt' } })

    expect(analyzeButton).not.toBeDisabled()
  })

  it('shows loading state when analyzing', async () => {
    mockFetch.mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              ok: true,
              json: async () => ({
                sentiment: {},
                brand_mentions: {},
                website_coverage: {},
                trust_score: {},
                analysis_id: 'test-id',
              }),
            })
          }, 100)
        })
    )

    render(<HomePage />)

    const textarea = screen.getByPlaceholderText(/Enter your prompt here/i)
    const analyzeButton = screen.getByRole('button', { name: /Analyze/i })

    fireEvent.change(textarea, { target: { value: 'Test prompt' } })
    fireEvent.click(analyzeButton)

    await waitFor(() => {
      expect(screen.getByText(/Analyzing.../i)).toBeInTheDocument()
    })
  })

  it('handles successful analysis', async () => {
    const mockResponse = {
      sentiment: { tone: 'positive' },
      brand_mentions: { count: 10 },
      website_coverage: { total_websites_crawled: 25 },
      trust_score: { ai_recommendations: 0.8 },
      analysis_id: 'test-id-123',
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    })

    render(<HomePage />)

    const textarea = screen.getByPlaceholderText(/Enter your prompt here/i)
    const analyzeButton = screen.getByRole('button', { name: /Analyze/i })

    fireEvent.change(textarea, { target: { value: 'Analyze Tesla brand' } })
    fireEvent.click(analyzeButton)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/analysis')
      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        'analysisResults',
        JSON.stringify(mockResponse)
      )
    })
  })

  it('handles analysis error', async () => {
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {})

    mockFetch.mockResolvedValue({
      ok: false,
      statusText: 'Internal Server Error',
    })

    render(<HomePage />)

    const textarea = screen.getByPlaceholderText(/Enter your prompt here/i)
    const analyzeButton = screen.getByRole('button', { name: /Analyze/i })

    fireEvent.change(textarea, { target: { value: 'Test prompt' } })
    fireEvent.click(analyzeButton)

    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith('Analysis failed. Please try again.')
    })

    alertSpy.mockRestore()
  })
})
