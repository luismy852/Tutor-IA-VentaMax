const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) throw new Error(`HTTP ${res.status} — ${path}`);
  return res.json();
}

export const api = {
  createSession: () =>
    request('/session', { method: 'POST' }),

  getSession: (sessionId) =>
    request(`/session/${sessionId}`),

  fetchQuestions: () =>
    request('/questions'),

  fetchHistory: (sessionId) =>
    request(`/history/${sessionId}`),

  streamQuestionFeedback: (sessionId, questionNum, question, response) =>
    fetch(`${BASE_URL}/retroalimentacion/${sessionId}/${questionNum}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, response }),
    }),

  streamEvaluationFeedback: (sessionId, questions, responses) =>
    fetch(`${BASE_URL}/retroalimentacion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, questions, responses }),
    }),

  streamChat: (sessionId, message) =>
    fetch(`${BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message }),
    }),
};
