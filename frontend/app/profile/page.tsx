import PrivateProfile from '../components/PrivateProfile';
import PrivateRoute from '../components/PrivateRoute';

export default function ProfilePage() {
  return (
    <PrivateRoute>
      <PrivateProfile />
    </PrivateRoute>
  );
}