import { useState, useCallback } from 'react';
import { api } from '../services/api';
import { QUESTION_COUNT } from '../config/constants';

export function useEvaluation({ sessionId, updateStoredState }) {
  const [questions, setQuestions] = useState([]);
  const [phase, setPhase] = useState('idle'); // idle | loading | active | streaming | completed
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [error, setError] = useState(null);

  const loadQuestions = useCallback(async () => {
    setPhase('loading');
    setError(null);
    try {
      const data = await api.fetchQuestions();
      setQuestions(data);
      setPhase('active');
      setCurrentIndex(0);
      setAnswers([]);
      updateStoredState({ evaluationPhase: 'active', currentQuestionIndex: 0 });
      return data;
    } catch {
      setError('No se pudieron cargar las preguntas. Intenta de nuevo.');
      setPhase('idle');
      return null;
    }
  }, [updateStoredState]);

  const submitAnswer = useCallback((text) => {
    if (phase !== 'active') return null;

    const newAnswers = [...answers, text];
    setAnswers(newAnswers);
    const nextIndex = currentIndex + 1;

    if (nextIndex < QUESTION_COUNT) {
      setCurrentIndex(nextIndex);
      updateStoredState({ currentQuestionIndex: nextIndex });
      return {
        type: 'feedback',
        questionNum: currentIndex + 1,
        question: questions[currentIndex],
        answer: text,
        nextIndex,
      };
    }

    setPhase('streaming');
    return { type: 'stream', questions, answers: newAnswers };
  }, [phase, answers, currentIndex, questions, updateStoredState]);

  const markCompleted = useCallback(() => {
    setPhase('completed');
    updateStoredState({ evaluationPhase: 'completed', state: 'chat' });
  }, [updateStoredState]);

  const reset = useCallback(() => {
    setQuestions([]);
    setPhase('idle');
    setCurrentIndex(0);
    setAnswers([]);
    setError(null);
  }, []);

  return { questions, phase, currentIndex, error, loadQuestions, submitAnswer, markCompleted, reset };
}
