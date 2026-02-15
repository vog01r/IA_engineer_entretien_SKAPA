import { useState, useRef, useEffect } from "react";
import { agentAPI } from "../services/api";

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const data = await agentAPI.ask(question);
      const answer = data.answer ?? "Pas de réponse.";
      setMessages((prev) => [...prev, { role: "assistant", content: answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Erreur : ${err.message || "Impossible de contacter l'agent."}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-base font-semibold mb-1" style={{ color: "var(--color-text)" }}>
        Chat
      </h2>
      <p className="text-sm mb-4" style={{ color: "var(--color-muted)" }}>
        Posez une question sur la météo.
      </p>

      <div
        className="h-72 overflow-y-auto rounded-lg p-3 mb-4"
        style={{ background: "var(--color-bg)", border: "1px solid var(--color-border)" }}
      >
        {messages.length === 0 && !loading && (
          <p className="text-sm py-2" style={{ color: "var(--color-muted)" }}>
            Par ex. : « Quel temps à Paris ? » ou « Tendances à Lyon »
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-2.5 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className="max-w-[85%] px-3.5 py-2 rounded-lg text-sm break-words whitespace-pre-wrap"
              style={
                msg.role === "user"
                  ? { background: "var(--color-accent)", color: "white" }
                  : { background: "var(--color-border)", color: "var(--color-text)" }
              }
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start mb-2.5">
            <span
              className="px-3.5 py-2 rounded-lg text-sm"
              style={{ background: "var(--color-border)", color: "var(--color-muted)" }}
            >
              Réflexion…
            </span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Votre question…"
          className="flex-1 skapa-input px-3 py-2 text-sm"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="skapa-btn skapa-btn-primary px-4 py-2 text-sm"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
