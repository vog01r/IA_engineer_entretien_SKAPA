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
    <div className="bg-white border border-gray-200 rounded-lg shadow p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-800">Chat Agent</h2>

      <div className="h-96 overflow-y-auto border border-gray-200 rounded-md p-3 mb-4 bg-gray-50">
        {messages.length === 0 && !loading && (
          <p className="text-gray-500 text-sm">Posez une question à l'agent météo.</p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-3 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start mb-3">
            <div className="bg-gray-200 text-gray-600 px-4 py-2 rounded-lg">
              Réflexion...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Votre question..."
          className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-md transition-colors"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
