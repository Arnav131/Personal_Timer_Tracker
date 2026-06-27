/* oxlint-disable react/only-export-components */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { isSupabaseConfigured, supabase } from '../lib/supabase';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(isSupabaseConfigured);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!supabase) return;
    let active = true;

    supabase.auth.getSession().then(({ data, error: sessionError }) => {
      if (!active) return;
      if (sessionError) setError(sessionError.message);
      setSession(data.session);
      setLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setLoading(false);
    });

    return () => {
      active = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  const signInWithGoogle = useCallback(async () => {
    if (!supabase) {
      setError('Google sign-in is not configured yet. Add the Supabase environment variables.');
      return;
    }
    setError('');
    const { error: signInError } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/` },
    });
    if (signInError) setError(signInError.message);
  }, []);

  const signOut = useCallback(async () => {
    if (!supabase) return;
    setError('');
    const { error: signOutError } = await supabase.auth.signOut();
    if (signOutError) setError(signOutError.message);
  }, []);

  const value = useMemo(() => ({
    user: session?.user ?? null,
    loading,
    error,
    configured: isSupabaseConfigured,
    signInWithGoogle,
    signOut,
  }), [session, loading, error, signInWithGoogle, signOut]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
