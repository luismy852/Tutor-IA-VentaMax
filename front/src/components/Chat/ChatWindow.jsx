import { useState, useCallback, useEffect, useRef } from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { EvaluationProgress } from './EvaluationProgress';
import { ConfirmModal } from './ConfirmModal';
import { useChatSession } from '../../hooks/useChatSession';
import { useEvaluation } from '../../hooks/useEvaluation';
import { useChatStream } from '../../hooks/useChatStream';
import { api } from '../../services/api';
import { QUESTION_COUNT } from '../../config/constants';
import './Chat.css';

const createMessage = (content, role) => ({
  id: crypto.randomUUID(),
  content,
  role,
});

export function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [showResetModal, setShowResetModal] = useState(false);
  const historyLoadedRef = useRef(false);
  const skipHistoryRef = useRef(false);

  const addMessage = useCallback((content, role) => {
    setMessages((prev) => [...prev, createMessage(content, role)]);
  }, []);

  const { sessionId, sessionState, setSessionState, loading, error, resetSession, updateStoredState } =
    useChatSession();

  const { questions, phase: evalPhase, currentIndex, error: evalError, loadQuestions, submitAnswer, markCompleted, reset: resetEval } =
    useEvaluation({ sessionId, updateStoredState });

  const { streamingMessage, isStreaming, error: streamError, sendMessage, readStream } = useChatStream({
    onMessageComplete: (aiResponse) => addMessage(aiResponse, 'assistant'),
  });

  useEffect(() => {
    if (sessionId && sessionState === 'evaluacion' && evalPhase === 'idle') {
      loadQuestions().then((qs) => {
        if (qs?.length > 0) {
          setMessages([
            createMessage(
              `¡Bienvenido a tu evaluación de ventas! Responderás ${QUESTION_COUNT} preguntas para analizar tu nivel.\n\nPregunta 1: ${qs[0]}`,
              'assistant'
            ),
          ]);
        }
      });
    }
  }, [sessionId, sessionState, evalPhase, loadQuestions]);

  useEffect(() => {
    if (sessionId && sessionState === 'chat' && !historyLoadedRef.current && !skipHistoryRef.current) {
      historyLoadedRef.current = true;
      api
        .fetchHistory(sessionId)
        .then((history) => {
          if (history.length > 0) {
            const loaded = [...history]
              .reverse()
              .flatMap((h) => [
                createMessage(h.user_message, 'user'),
                createMessage(h.ai_response, 'assistant'),
              ]);
            setMessages(loaded);
          }
        })
        .catch(() => {
          /* no es crítico: se inicia con historial vacío */
        });
    }
  }, [sessionId, sessionState]);

  const handleSendMessage = useCallback(
    async (text) => {
      if (evalPhase === 'active') {
        addMessage(text, 'user');
        const result = submitAnswer(text);

        if (result?.type === 'feedback') {
          await readStream(
            api.streamQuestionFeedback(sessionId, result.questionNum, result.question, result.answer)
          );
          addMessage(`Pregunta ${result.nextIndex + 1}: ${questions[result.nextIndex]}`, 'assistant');
        } else if (result?.type === 'stream') {
          await readStream(
            api.streamQuestionFeedback(
              sessionId,
              QUESTION_COUNT,
              result.questions[QUESTION_COUNT - 1],
              result.answers[QUESTION_COUNT - 1]
            )
          );
          await readStream(
            api.streamEvaluationFeedback(sessionId, result.questions, result.answers),
            (feedback) => {
              addMessage(feedback, 'assistant');
              skipHistoryRef.current = true;
              markCompleted();
              setSessionState('chat');
            }
          );
        }
      } else if (sessionState === 'chat') {
        addMessage(text, 'user');
        await sendMessage(sessionId, text);
      }
    },
    [evalPhase, sessionState, sessionId, addMessage, submitAnswer, sendMessage, questions, readStream, markCompleted, setSessionState]
  );

  const handleReset = useCallback(async () => {
    setMessages([]);
    historyLoadedRef.current = false;
    skipHistoryRef.current = false;
    resetEval();
    await resetSession();
  }, [resetEval, resetSession]);

  const handleConfirmReset = useCallback(async () => {
    setShowResetModal(false);
    await handleReset();
  }, [handleReset]);

  const displayError = error || evalError || streamError;
  const isEvaluation = sessionState === 'evaluacion' && evalPhase === 'active';
  const isBusy = isStreaming || evalPhase === 'loading' || evalPhase === 'streaming';

  if (loading) {
    return (
      <div className="chat-window">
        <div className="chat-loading">Cargando sesión...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chat-window">
        <div className="chat-error">
          <p>{error}</p>
          <button onClick={handleReset}>Reintentar</button>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h3>Tutor IA — VentaMax</h3>
        <div className="chat-header-right">
          <span className="chat-status">
            {isEvaluation ? (
              <span className="evaluation-badge">Evaluación</span>
            ) : (
              `Sesión: ${sessionId?.slice(0, 8)}...`
            )}
          </span>
          <button className="new-chat-btn" onClick={() => setShowResetModal(true)}>
            Nuevo Chat
          </button>
        </div>
      </div>

      {isEvaluation && <EvaluationProgress currentIndex={currentIndex} />}

      {displayError && <div className="chat-inline-error">{displayError}</div>}

      <MessageList messages={messages} streamingMessage={streamingMessage} />

      <ChatInput
        onSend={handleSendMessage}
        disabled={isBusy}
        placeholder={
          isEvaluation
            ? `Responde la pregunta ${Math.min(currentIndex + 1, QUESTION_COUNT)}...`
            : 'Escribe tu mensaje...'
        }
      />

      {showResetModal && (
        <ConfirmModal
          message="Si continúas, se perderá la conversación actual. ¿Deseas empezar de nuevo?"
          onConfirm={handleConfirmReset}
          onCancel={() => setShowResetModal(false)}
        />
      )}
    </div>
  );
}
