import ReactMarkdown from 'react-markdown';

export function Message({ content, role, isStreaming }) {
  const isUser = role === 'user';

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-ai'}`}>
      <div className="message-bubble">
        {isUser ? (
          <p>{content}</p>
        ) : (
          <ReactMarkdown>{content}</ReactMarkdown>
        )}
        {isStreaming && <span className="streaming-indicator">▊</span>}
      </div>
    </div>
  );
}
