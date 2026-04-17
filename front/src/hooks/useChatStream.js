import { useState, useCallback } from 'react';
import { api } from '../services/api';

export function useChatStream({ onMessageComplete } = {}) {
  const [streamingMessage, setStreamingMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);

  const readStream = useCallback(async (fetchPromise, onComplete) => {
    setIsStreaming(true);
    setStreamingMessage('');
    setError(null);

    try {
      const response = await fetchPromise;
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ') && line.slice(6) !== '') {
            fullResponse += line.slice(6).replace(/\\n/g, '\n');
            setStreamingMessage(fullResponse);
          }
        }
      }

      setStreamingMessage('');
      const handler = onComplete ?? onMessageComplete;
      handler?.(fullResponse);
      return fullResponse;
    } catch {
      setError('No se pudo obtener la respuesta. Intenta de nuevo.');
      setStreamingMessage('');
    } finally {
      setIsStreaming(false);
    }
  }, [onMessageComplete]);

  const sendMessage = useCallback(async (sessionId, text) => {
    await readStream(api.streamChat(sessionId, text));
  }, [readStream]);

  return { streamingMessage, isStreaming, error, sendMessage, readStream };
}
