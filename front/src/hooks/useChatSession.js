import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { STORAGE_KEY } from '../config/constants';

export function useChatSession() {
  const [sessionId, setSessionId] = useState(null);
  const [sessionState, setSessionState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const saveToStorage = useCallback((data) => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch { /* unavailable */ }
  }, []);

  const loadFromStorage = useCallback(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch { return null; }
  }, []);

  const clearStorage = useCallback(() => {
    try { localStorage.removeItem(STORAGE_KEY); } catch { /* unavailable */ }
  }, []);

  const updateStoredState = useCallback((patch) => {
    const stored = loadFromStorage() || {};
    saveToStorage({ ...stored, ...patch });
  }, [loadFromStorage, saveToStorage]);

  const createSession = useCallback(async () => {
    setError(null);
    try {
      const data = await api.createSession();
      setSessionId(data.session_id);
      setSessionState(data.state);
      saveToStorage({ sessionId: data.session_id, state: data.state });
      return data;
    } catch {
      setError('No se pudo conectar al servidor. Intenta de nuevo.');
      return null;
    }
  }, [saveToStorage]);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      const stored = loadFromStorage();
      if (stored?.sessionId) {
        try {
          const session = await api.getSession(stored.sessionId);
          setSessionId(session.session_id);
          setSessionState(session.state);
          saveToStorage({ ...stored, state: session.state });
        } catch {
          clearStorage();
          await createSession();
        }
      } else {
        await createSession();
      }
      setLoading(false);
    };
    init();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const resetSession = useCallback(async () => {
    clearStorage();
    setSessionId(null);
    setSessionState(null);
    return createSession();
  }, [clearStorage, createSession]);

  return {
    sessionId,
    sessionState,
    setSessionState,
    loading,
    error,
    resetSession,
    updateStoredState,
  };
}
