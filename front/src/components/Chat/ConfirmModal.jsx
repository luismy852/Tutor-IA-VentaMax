export function ConfirmModal({ message, onConfirm, onCancel }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="modal-btn-cancel" onClick={onCancel}>Cancelar</button>
          <button className="modal-btn-confirm" onClick={onConfirm}>Empezar de nuevo</button>
        </div>
      </div>
    </div>
  );
}
