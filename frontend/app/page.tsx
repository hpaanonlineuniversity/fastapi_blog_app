import Home from './components/Home';
import PrivateRoute from './components/PrivateRoute';

export default function HomePage() {
  return (
    <PrivateRoute>
      <Home />
    </PrivateRoute>
  );
}