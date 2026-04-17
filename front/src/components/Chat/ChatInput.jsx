import { useState } from 'react';

export function ChatInput({ onSend, disabled, placeholder = 'Escribe tu mensaje...' }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <input
        type="text"
        className="chat-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
      />
      <button type="submit" className="chat-send-btn" disabled={disabled || !message.trim()}>
        Enviar
      </button>
    </form>
  );
}
