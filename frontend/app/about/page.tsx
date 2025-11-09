import About from '../components/About';
import PrivateRoute from '../components/PrivateRoute';

export default function AboutPage() {
  return (
    <PrivateRoute>
      <About />
    </PrivateRoute>
  );
}