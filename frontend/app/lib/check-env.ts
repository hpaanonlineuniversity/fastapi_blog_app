// lib/check-env.ts
export function checkSupabaseConfig() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  console.log('🔧 Environment Check:');
  console.log('NEXT_PUBLIC_SUPABASE_URL:', supabaseUrl ? '✅ Loaded' : '❌ Missing');
  console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY:', supabaseKey ? '✅ Loaded' : '❌ Missing');
  
  if (!supabaseUrl || !supabaseKey) {
    throw new Error('Supabase environment variables are not properly configured');
  }

  // Check if key looks valid (starts with eyJ for JWT)
  if (!supabaseKey.startsWith('eyJ')) {
    console.warn('⚠️  Supabase key may be invalid - should start with "eyJ"');
  }

  return true;
}

// Call this in your app
checkSupabaseConfig();