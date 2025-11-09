import UpdatePost from '../../components/UpdatePost';
import OnlyAdminPrivateRoute from '../../components/OnlyAdminPrivateRoute';

interface UpdatePostPageProps {
  params: {
    postId: string;
  };
}

export default function UpdatePostPage({ params }: UpdatePostPageProps) {
  return (
    <OnlyAdminPrivateRoute>
      <UpdatePost postId={params.postId} />
    </OnlyAdminPrivateRoute>
  );
}