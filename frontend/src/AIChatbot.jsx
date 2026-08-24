import { useState } from "react";
import API from "./api";


// ============================================================
// AI CHATBOT
// ============================================================

function AIChatbot() {

  const [open, setOpen] = useState(false);

  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi 👋 I'm ReFindX AI Assistant. How can I help you?",
    },
  ]);

  const [loading, setLoading] = useState(false);


  // ==========================================================
  // SEND MESSAGE
  // ==========================================================

  const sendMessage = async (event) => {

    event.preventDefault();

    const text = message.trim();

    if (!text || loading) {
      return;
    }


    // Show user message immediately

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: text,
      },
    ]);


    setMessage("");
    setLoading(true);


    try {

      const response = await API.post(
        "/api/chatbot/chat",
        {
          message: text,
        }
      );


      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text:
            response.data.reply ||
            "Sorry, I could not understand that.",
        },
      ]);


    } catch (error) {

      console.error(
        "ReFindX chatbot error:",
        error
      );


      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text:
            "Sorry 😔 Something went wrong. Please try again.",
        },
      ]);


    } finally {

      setLoading(false);

    }
  };


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <>
      {open && (

        <div className="ai-chat-window">

          {/* HEADER */}

          <div className="ai-chat-header">

            <div className="ai-chat-title">

              <span className="ai-chat-icon">
                🤖
              </span>

              <div>
                <strong>
                  ReFindX AI
                </strong>

                <small>
                  AI Assistant
                </small>
              </div>

            </div>


            <button
              type="button"
              className="ai-close-btn"
              onClick={() => setOpen(false)}
            >
              ×
            </button>

          </div>


          {/* MESSAGES */}

          <div className="ai-chat-messages">

            {messages.map((item, index) => (

              <div
                key={index}
                className={
                  item.role === "user"
                    ? "ai-message user-message"
                    : "ai-message bot-message"
                }
              >
                {item.text}
              </div>

            ))}


            {loading && (

              <div className="ai-message bot-message">
                🤖 Thinking...
              </div>

            )}

          </div>


          {/* INPUT */}

          <form
            className="ai-chat-input"
            onSubmit={sendMessage}
          >

            <input
              type="text"
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              placeholder="Ask ReFindX..."
              disabled={loading}
            />


            <button
              type="submit"
              disabled={
                loading ||
                !message.trim()
              }
            >
              ➤
            </button>

          </form>

        </div>

      )}


      {/* FLOATING BUTTON */}

      <button
        type="button"
        className="ai-chat-button"
        onClick={() =>
          setOpen((previous) => !previous)
        }
        aria-label="Open ReFindX AI Assistant"
      >
        {open ? "×" : "🤖"}
      </button>

    </>
  );
}


export default AIChatbot;