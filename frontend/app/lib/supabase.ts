// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_URL

// Add validation
if (!supabaseUrl || !supabaseKey) {
  throw new Error('Supabase environment variables are missing')
}

console.log('Supabase URL:', supabaseUrl ? 'Loaded' : 'Missing');
console.log('Supabase Key:', supabaseKey ? 'Loaded' : 'Missing');

export const supabase = createClient(supabaseUrl, supabaseKey)