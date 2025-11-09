import Search from '../components/Search';
import PrivateRoute from '../components/PrivateRoute';

export default function SearchPage() {
  return (
    <PrivateRoute>
      <Search />
    </PrivateRoute>
  );
}