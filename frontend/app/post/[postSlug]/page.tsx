import PostPage from '../../components/PostPage';

interface PostPageProps {
  params: Promise<{
    postSlug: string;
  }>;
}

export default async function PostSlugPage({ params }: PostPageProps) {
  const { postSlug } = await params;
  
  return <PostPage postSlug={postSlug} />;
}