import { ChatHeader }   from "../components/ChatHeader";
import { ChatInput }    from "../components/Chatinput";
import { EmptyState }   from "../components/EmptyState";
import { Message }      from "../components/Message";
import { TypingDots }   from "../components/Typingdots";
import { useChat }      from "../hooks/useChat";
import { useApiStatus } from "../hooks/useApiStatus";

// pages/ChatPage.tsx
import { API_BASE_URL } from "../services/ragService"; // or wherever it's imported

console.log("API BASE:", import.meta.env.VITE_API_BASE_URL);
console.log("API BASE URL:", API_BASE_URL);

/**
 * ChatPage
 *
 * The single page of the app. Its only job is to wire the two hooks to
 * the components — no business logic lives here.
 */
export default function ChatPage(): React.ReactElement {
  const { apiStatus, totalChunks } = useApiStatus();

  const {
    messages,
    input,
    setInput,
    loading,
    sendQuestion,
    handleKey,
    bottomRef,
    inputRef,
  } = useChat();

  return (
  <div className="mx-auto flex h-full w-full max-w-6xl flex-col">
  <ChatHeader
    apiStatus={apiStatus}
    totalChunks={totalChunks}
  />

      <main className="min-h-0 flex-1 overflow-y-auto px-6 py-6">
      {messages.length === 0 && (
        <EmptyState onSuggest={sendQuestion} />
      )}

      {messages.map((m, i) => (
        <Message key={i} msg={m} />
      ))}

      {loading && <TypingDots />}

      <div ref={bottomRef} className="h-5" />
    </main>

    <ChatInput
      input={input}
      setInput={setInput}
      loading={loading}
      onSend={() => sendQuestion()}
      onKeyDown={handleKey}
      inputRef={inputRef}
    />
  </div>
);
}