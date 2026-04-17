import { QUESTION_COUNT } from '../../config/constants';

export function EvaluationProgress({ currentIndex }) {
  const displayed = Math.min(currentIndex + 1, QUESTION_COUNT);
  return (
    <div className="evaluation-progress">
      Pregunta {displayed} de {QUESTION_COUNT}
    </div>
  );
}
