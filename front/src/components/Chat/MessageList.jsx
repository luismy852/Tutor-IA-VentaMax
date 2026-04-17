import { useEffect, useRef } from 'react';
import { Message } from './Message';

export function MessageList({ messages, streamingMessage }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, streamingMessage]);

  return (
    <div className="message-list">
      {messages.map((msg) => (
        <Message key={msg.id} content={msg.content} role={msg.role} />
      ))}
      {streamingMessage && (
        <Message content={streamingMessage} role="assistant" isStreaming />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
