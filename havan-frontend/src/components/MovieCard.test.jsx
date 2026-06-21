import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import MovieCard from './MovieCard';
import * as AuthContext from '../context/AuthContext';

// Mock the CSS
vi.mock('../index.css', () => ({}));

describe('MovieCard', () => {
  const mockMovie = {
    id: 1,
    title: 'Inception',
    thumbnail_url: 'http://example.com/inception.jpg',
    is_in_watchlist: false,
    rating: 'PG-13',
    release_year: 2010,
    duration_mins: 148,
  };

  const mockOnPlay = vi.fn();
  const mockOnWatchlistToggle = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock the useAuth hook
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
      user: { username: 'testuser' },
      authFetch: vi.fn().mockResolvedValue({ ok: true, status: 201 }),
      API: 'http://localhost:8000/api',
    });
  });

  it('renders movie title and poster', () => {
    render(<MovieCard movie={mockMovie} onPlay={mockOnPlay} onWatchlistToggle={mockOnWatchlistToggle} />);
    
    // Check if image is rendered
    const img = screen.getByAltText('Inception');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'http://example.com/inception.jpg');
    
    // Check if title is rendered
    expect(screen.getByText('Inception')).toBeInTheDocument();
  });

  it('formats duration correctly', () => {
    render(<MovieCard movie={mockMovie} onPlay={mockOnPlay} onWatchlistToggle={mockOnWatchlistToggle} />);
    expect(screen.getByText('2h 28m')).toBeInTheDocument();
  });

  it('calls onPlay when Play button is clicked', () => {
    render(<MovieCard movie={mockMovie} onPlay={mockOnPlay} onWatchlistToggle={mockOnWatchlistToggle} />);
    const playBtn = screen.getByText('▶ Play Now');
    fireEvent.click(playBtn);
    expect(mockOnPlay).toHaveBeenCalledWith(mockMovie);
  });
});
