import CreatePost from '../components/CreatePost';
import OnlyAdminPrivateRoute from '../components/OnlyAdminPrivateRoute';

export default function CreatePostPage() {
  return (
    <OnlyAdminPrivateRoute>
      <CreatePost />
    </OnlyAdminPrivateRoute>
  );
}