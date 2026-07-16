import { render, screen } from '@testing-library/react'; import { MemoryRouter } from 'react-router-dom'; import { LandingPage } from './LandingPage';
test('renders landing page',()=>{render(<MemoryRouter><LandingPage/></MemoryRouter>);expect(screen.getByText(/operating system for AI teams/i)).toBeInTheDocument();});
