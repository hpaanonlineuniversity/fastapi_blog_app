import Projects from '../components/Projects';
import PrivateRoute from '../components/PrivateRoute';

export default function ProjectsPage() {
  return (
    <PrivateRoute>
      <Projects />
    </PrivateRoute>
  );
}
