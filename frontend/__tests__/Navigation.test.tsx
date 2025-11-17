import { render, screen } from '@testing-library/react'
import Navigation from '@/components/Navigation'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/'),
}))

describe('Navigation', () => {
  it('renders the navigation bar', () => {
    render(<Navigation />)

    expect(screen.getByText('Arrakis')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(<Navigation />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
