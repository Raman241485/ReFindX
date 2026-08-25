import { useEffect, useState } from "react";

import {
  Routes,
  Route,
  Link,
  useNavigate,
  useParams,
  useLocation,
} from "react-router-dom";
import AIChatbot from "./AIChatbot";

import API from "./api";


// ============================================================
// NAVBAR
// ============================================================

function Navbar({
  user,
  setUser,
  darkMode,
  setDarkMode,
}) {

  const navigate = useNavigate();
  const location = useLocation();


  // ==========================================================
  // LOGOUT
  // ==========================================================

  const logout = () => {

    localStorage.removeItem(
      "refindx_token"
    );

    localStorage.removeItem(
      "refindx_user"
    );

    setUser(null);

    navigate("/login");
  };


  // ==========================================================
  // NAVBAR
  // ==========================================================

  return (

    <nav className="navbar">

      {/* ====================================================
          LOGO
          ==================================================== */}

      <Link
        to="/"
        className="brand"
      >

        <img
          src="/refindx-logo.png"
          alt="ReFindX"
          className="brand-logo"
        />

        <span className="brand-name">
          {/* ReFind<span>X</span> */}
        </span>

      </Link>


      {/* ====================================================
          NAV LINKS
          ==================================================== */}

      <div className="nav-links">

        <Link
          className={
            location.pathname === "/"
              ? "active"
              : ""
          }
          to="/"
        >
          Home
        </Link>


        <Link to="/report">
          Report Item
        </Link>


        {user && (

          <Link to="/notifications">
            🔔 Notifications
          </Link>

        )}


        {user && (

          <Link to="/claims">
            My Claims
          </Link>

        )}


        {user?.role === "admin" && (

          <Link to="/admin">
            🛡️ Admin
          </Link>

        )}

      </div>


      {/* ====================================================
          ACCOUNT + DARK MODE
          ==================================================== */}

      <div className="nav-account">


        {/* ==================================================
            DARK MODE SWITCH
            ================================================== */}

        <button
          type="button"
          className={`theme-switch ${
            darkMode ? "dark" : ""
          }`}
          onClick={() =>
            setDarkMode(
              (previous) => !previous
            )
          }
          aria-label={
            darkMode
              ? "Switch to light mode"
              : "Switch to dark mode"
          }
          title={
            darkMode
              ? "Switch to Light Mode"
              : "Switch to Dark Mode"
          }
        >

          <span className="theme-icon">
            {darkMode ? "☀️" : "🌙"}
          </span>

        </button>


        {/* ==================================================
            LOGGED-IN USER
            ================================================== */}

        {user ? (

          <>

            <span className="user-badge">
              {user.name}
            </span>


            <button
              className="logout-btn"
              onClick={logout}
            >
              Logout
            </button>

          </>

        ) : (

          /* ==================================================
             LOGGED-OUT USER
             ================================================== */

          <>

            <Link
              className="login-btn"
              to="/login"
            >
              Login
            </Link>


            <Link
              className="signup-btn"
              to="/signup"
            >
              Sign Up
            </Link>

          </>

        )}

      </div>

    </nav>

  );
}
// ============================================================
// HOME
// ============================================================

function Home() {

  const [items, setItems] =
    useState([]);

  const [search, setSearch] =
    useState("");

  const [type, setType] =
    useState("");

  const [category, setCategory] =
    useState("");

  const [location, setLocation] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  const loadItems = async () => {

    try {

      setLoading(true);

      const response =
        await API.get(
          "/api/items/",
          {
            params: {
              search:
                search || undefined,

              type:
                type || undefined,

              category:
                category || undefined,

              location:
                location || undefined,
            },
          }
        );


      setItems(
        response.data
      );

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {

    loadItems();

  }, []);


  return (

    <div>

      <section className="hero">

        <div className="hero-content">

          <div className="hero-tag">
            AI POWERED LOST & FOUND
          </div>


          <h1>
            Lost something?
            <br />

            <span>
              Find it again.
            </span>
          </h1>


          <p>
            ReFindX uses AI image matching
            to connect lost and found items
            faster and smarter.
          </p>


          <div className="hero-actions">

            <Link
              to="/report"
              className="primary-btn"
            >
              + Report an Item
            </Link>


            <a
              href="#feed"
              className="secondary-btn"
            >
              Browse Items
            </a>

          </div>

        </div>

      </section>


      <section
        id="feed"
        className="feed-section"
      >

        <div className="section-heading">

          <div>

            <span className="section-label">
              COMMUNITY FEED
            </span>

            <h2>
              Recently verified items
            </h2>

          </div>

        </div>


        <div className="filters">

          <input
            placeholder="Search item..."
            value={search}
            onChange={(e) =>
              setSearch(
                e.target.value
              )
            }
          />


          <select
            value={type}
            onChange={(e) =>
              setType(
                e.target.value
              )
            }
          >

            <option value="">
              All
            </option>

            <option value="lost">
              Lost
            </option>

            <option value="found">
              Found
            </option>

          </select>


          <input
            placeholder="Category"
            value={category}
            onChange={(e) =>
              setCategory(
                e.target.value
              )
            }
          />


          <input
            placeholder="Location"
            value={location}
            onChange={(e) =>
              setLocation(
                e.target.value
              )
            }
          />


          <button
            className="search-btn"
            onClick={loadItems}
          >
            Search
          </button>

        </div>


        {loading ? (

          <div className="empty-state">
            Loading items...
          </div>

        ) : items.length === 0 ? (

          <div className="empty-state">

            <div className="empty-icon">
              🔎
            </div>

            <h3>
              No verified items found
            </h3>

            <p>
              Try another search or
              check back later.
            </p>

          </div>

        ) : (

          <div className="item-grid">

            {items.map(
              (item) => (

                <ItemCard
                  key={item.id}
                  item={item}
                />

              )
            )}

          </div>

        )}

      </section>

    </div>
  );
}


// ============================================================
// ITEM CARD
// ============================================================

function ItemCard({ item }) {
  const imageUrl =
    item.image_url
    ?
    `https://refindx.onrender.com${item.image_url}`
    : null;

  return (

    <Link
      to={`/items/${item.id}`}
      className="item-card-link"
    >

      <div className="item-card">

        <div className="item-image">

          {imageUrl ? (

            <img
              src={imageUrl}
              alt={item.title}
            />

          ) : (

            <div className="no-image">
              No Image
            </div>

          )}


          <span
            className={
              item.type === "lost"
                ? "status lost"
                : "status found"
            }
          >

            {item.type === "lost"
              ? "LOST"
              : "FOUND"}

          </span>

        </div>


        <div className="item-body">

          <h3>
            {item.title}
          </h3>


          <p className="category">
            {item.category}
          </p>


          <p>
            {item.description}
          </p>


          <div className="item-meta">

            <span>
              📍 {item.location}
            </span>


            <span>
              📅 {item.date_lost_found}
            </span>

          </div>


          <div className="view-item">
            View Details →
          </div>

        </div>

      </div>

    </Link>
  );
}



// ============================================================
// AI CHATBOT
// ============================================================

// function AIChatbot() {

//   const [open, setOpen] =
//     useState(false);

//   const [message, setMessage] =
//     useState("");

//   const [messages, setMessages] =
//     useState([
//       {
//         role: "assistant",
//         text:
//           "Hi 👋 I'm ReFindX AI Assistant. How can I help you?"
//       }
//     ]);

//   const [loading, setLoading] =
//     useState(false);


//   // ==========================================================
//   // SEND MESSAGE
//   // ==========================================================

//   const sendMessage = async (e) => {

//     e.preventDefault();

//     const text =
//       message.trim();

//     if (!text || loading) {
//       return;
//     }


//     // Add user message

//     setMessages(
//       (previous) => [
//         ...previous,
//         {
//           role: "user",
//           text: text,
//         },
//       ]
//     );


//     setMessage("");

//     setLoading(true);


//     try {

//       const response =
//         await API.post(
//           "/api/chatbot/chat",
//           {
//             message: text,
//           }
//         );


//       setMessages(
//         (previous) => [
//           ...previous,
//           {
//             role: "assistant",
//             text:
//               response.data.reply,
//           },
//         ]
//       );

//     } catch (error) {

//       console.error(
//         "Chatbot error:",
//         error
//       );


//       setMessages(
//         (previous) => [
//           ...previous,
//           {
//             role: "assistant",
//             text:
//               "Sorry 😔 I couldn't process your request right now.",
//           },
//         ]
//       );

//     } finally {

//       setLoading(false);

//     }
//   };


//   return (

//     <>
//       {/* ====================================================
//           CHAT WINDOW
//       ==================================================== */}

//       {open && (

//         <div className="ai-chat-window">

//           {/* HEADER */}

//           <div className="ai-chat-header">

//             <div>

//               <strong>
//                 🤖 ReFindX AI
//               </strong>

//               <small>
//                 AI Assistant
//               </small>

//             </div>


//             <button
//               onClick={() =>
//                 setOpen(false)
//               }
//             >
//               ×
//             </button>

//           </div>


//           {/* MESSAGES */}

//           <div className="ai-chat-messages">

//             {messages.map(
//               (msg, index) => (

//                 <div
//                   key={index}
//                   className={
//                     msg.role === "user"
//                       ? "ai-message user-message"
//                       : "ai-message bot-message"
//                   }
//                 >
//                   {msg.text}
//                 </div>

//               )
//             )}


//             {loading && (

//               <div
//                 className="ai-message bot-message"
//               >
//                 🤖 Thinking...
//               </div>

//             )}

//           </div>


//           {/* INPUT */}

//           <form
//             className="ai-chat-input"
//             onSubmit={sendMessage}
//           >

//             <input
//               value={message}
//               onChange={(e) =>
//                 setMessage(
//                   e.target.value
//                 )
//               }
//               placeholder="Ask ReFindX..."
//               disabled={loading}
//             />


//             <button
//               type="submit"
//               disabled={
//                 loading ||
//                 !message.trim()
//               }
//             >
//               ➤
//             </button>

//           </form>

//         </div>

//       )}


//       {/* ====================================================
//           FLOATING BUTTON
//       ==================================================== */}

//       <button
//         className="ai-chat-button"
//         onClick={() =>
//           setOpen(
//             (previous) =>
//               !previous
//           )
//         }
//         aria-label="Open ReFindX AI"
//       >

//         {open
//           ? "×"
//           : "🤖"}

//       </button>

//     </>

//   );
// }

// ============================================================
// ITEM DETAILS
// ============================================================

function ItemDetails({ user }) {

  const { itemId } =
    useParams();

  const navigate =
    useNavigate();


  // ==========================================================
  // ITEM STATES
  // ==========================================================

  const [item, setItem] =
    useState(null);

  const [loading, setLoading] =
    useState(true);


  // ==========================================================
  // CLAIM STATES
  // ==========================================================

  const [proof, setProof] =
    useState("");

  const [claimLoading, setClaimLoading] =
    useState(false);


  // ==========================================================
  // DELETE STATES
  // ==========================================================

  const [deleteLoading, setDeleteLoading] =
    useState(false);


  // ==========================================================
  // AI MATCHING STATES
  // ==========================================================

  const [aiLoading, setAiLoading] =
    useState(false);

  const [aiMatches, setAiMatches] =
    useState([]);

  const [aiMessage, setAiMessage] =
    useState("");

  const [aiError, setAiError] =
    useState("");


  // ==========================================================
  // CLAIM MESSAGE
  // ==========================================================

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");


  // ==========================================================
  // CONTACT OWNER STATES
  // ==========================================================

  const [contactOpen, setContactOpen] =
    useState(false);

  const [contactMessage, setContactMessage] =
    useState("");

  const [contactLoading, setContactLoading] =
    useState(false);

  const [contactSuccess, setContactSuccess] =
    useState("");

  const [contactError, setContactError] =
    useState("");


  // ==========================================================
  // LOAD ITEM
  // ==========================================================

  useEffect(() => {

    const loadItem = async () => {

      try {

        const response =
          await API.get(
            `/api/items/${itemId}`
          );

        setItem(
          response.data
        );

      } catch (error) {

        setError(
          error.response?.data?.detail ||
          "Item not found"
        );

      } finally {

        setLoading(false);

      }
    };


    loadItem();

  }, [itemId]);


  // ==========================================================
  // SUBMIT CLAIM
  // ==========================================================

  const submitClaim = async (e) => {

    e.preventDefault();

    setError("");
    setMessage("");


    if (!user) {

      navigate("/login");

      return;
    }


    if (!proof.trim()) {

      setError(
        "Please provide proof of ownership."
      );

      return;
    }


    try {

      setClaimLoading(true);


      const response =
        await API.post(
          "/api/claims/",
          null,
          {
            params: {
              item_id: item.id,
              proof: proof,
            },
          }
        );


      setMessage(
        response.data.message +
        " Your claim is now pending admin review."
      );


      setProof("");

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not submit claim."
      );

    } finally {

      setClaimLoading(false);

    }
  };


  // ==========================================================
  // DELETE ITEM - ADMIN ONLY
  // ==========================================================

  const deleteItem = async () => {

    if (user?.role !== "admin") {
      return;
    }


    const confirmed =
      window.confirm(
        `Are you sure you want to permanently delete "${item.title}"?`
      );


    if (!confirmed) {
      return;
    }


    try {

      setDeleteLoading(true);

      setError("");
      setMessage("");


      await API.delete(
        `/api/admin/items/${item.id}`
      );


      alert(
        "Item deleted successfully."
      );


      navigate("/");

    } catch (error) {

      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Could not delete item."
      );

    } finally {

      setDeleteLoading(false);

    }
  };


  // ==========================================================
  // RUN AI MATCHING
  // ==========================================================

  const runAIMatching = async () => {

    if (!item) {
      return;
    }


    try {

      setAiLoading(true);

      setAiMatches([]);

      setAiMessage("");

      setAiError("");


      const response =
        await API.post(
          `/api/ai/match/${item.id}`
        );


      setAiMatches(
        response.data.matches || []
      );


      setAiMessage(
        response.data.message ||
        "AI matching completed."
      );

    } catch (error) {

      console.error(error);

      setAiError(
        error.response?.data?.detail ||
        "Could not run AI matching."
      );

    } finally {

      setAiLoading(false);

    }
  };


  // ==========================================================
  // CONTACT OWNER VIA EMAIL
  // ==========================================================

  const contactOwner = async (e) => {

    e.preventDefault();

    setContactSuccess("");
    setContactError("");


    // --------------------------------------------------------
    // LOGIN CHECK
    // --------------------------------------------------------

    if (!user) {

      navigate("/login");

      return;
    }


    // --------------------------------------------------------
    // MESSAGE CHECK
    // --------------------------------------------------------

    if (!contactMessage.trim()) {

      setContactError(
        "Please write a message before sending."
      );

      return;
    }


    // --------------------------------------------------------
    // PREVENT CONTACTING YOUR OWN ITEM
    // --------------------------------------------------------

    if (
      user.id === item.user_id
    ) {

      setContactError(
        "You cannot contact yourself about your own item."
      );

      return;
    }


    try {

      setContactLoading(true);


      const response =
        await API.post(
          `/api/contact/item/${item.id}`,
          {
            message:
              contactMessage.trim(),
          }
        );


      setContactSuccess(
        response.data.message ||
        "Message sent successfully."
      );


      setContactMessage("");


      // Close form after successful email

      setTimeout(() => {

        setContactOpen(false);

      }, 1500);

    } catch (error) {

      console.error(
        "Contact owner error:",
        error
      );


      setContactError(
        error.response?.data?.detail ||
        "Could not send message.  Please try again."
      );

    } finally {

      setContactLoading(false);

    }
  };


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (

      <div className="empty-state">
        Loading item...
      </div>

    );

  }


  // ==========================================================
  // ITEM NOT FOUND
  // ==========================================================

  if (!item) {

    return (

      <div className="empty-state">

        <h2>
          Item not found
        </h2>


        <p>
          {error}
        </p>

      </div>

    );

  }


  // ==========================================================
  // IMAGE URL
  // ==========================================================

  const imageUrl =
  item.image_url
    ?
    `https://refindx.onrender.com${item.image_url}`
    : null;


  // ==========================================================
  // PAGE
  // ==========================================================

  return (

    <div className="item-details-page">


      {/* ====================================================
          BACK BUTTON
      ==================================================== */}

      <button
        className="back-btn"
        onClick={() =>
          navigate(-1)
        }
      >
        ← Back
      </button>


      {/* ====================================================
          ADMIN DELETE
      ==================================================== */}

      {user?.role === "admin" && (

        <div
          style={{
            marginBottom: "20px",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >

          <button
            onClick={deleteItem}
            disabled={deleteLoading}
            style={{
              background: "#dc2626",
              color: "white",
              border: "none",
              borderRadius: "8px",
              padding: "12px 20px",
              cursor:
                deleteLoading
                  ? "not-allowed"
                  : "pointer",
              fontWeight: "700",
              opacity:
                deleteLoading
                  ? 0.7
                  : 1,
            }}
          >

            {deleteLoading
              ? "Deleting..."
              : "🗑️ Delete Item"}

          </button>

        </div>

      )}


      {/* ====================================================
          ERROR
      ==================================================== */}

      {error && (

        <div className="error-box">
          {error}
        </div>

      )}


      <div className="item-details-grid">


        {/* ==================================================
            IMAGE
        ================================================== */}

        <div className="details-image">

          {imageUrl ? (

            <img
              src={imageUrl}
              alt={item.title}
            />

          ) : (

            <div className="no-image">
              No Image
            </div>

          )}

        </div>


        {/* ==================================================
            DETAILS
        ================================================== */}

        <div className="details-content">


          {/* ITEM TYPE */}

          <span
            className={
              item.type === "lost"
                ? "detail-type lost-type"
                : "detail-type found-type"
            }
          >

            {item.type === "lost"
              ? "LOST ITEM"
              : "FOUND ITEM"}

          </span>


          {/* TITLE */}

          <h1>
            {item.title}
          </h1>


          {/* CATEGORY */}

          <p className="detail-category">
            {item.category}
          </p>


          {/* DESCRIPTION */}

          <p className="detail-description">
            {item.description}
          </p>


          {/* ==================================================
              ITEM INFORMATION
          ================================================== */}

          <div className="details-info">

            <div>

              <span>
                Location
              </span>

              <strong>
                📍 {item.location}
              </strong>

            </div>


            <div>

              <span>
                Date
              </span>

              <strong>
                📅 {item.date_lost_found}
              </strong>

            </div>

          </div>


          {/* ==================================================
              CONTACT OWNER
          ================================================== */}

          {user &&
            item.type === "found" &&
            user.id !== item.user_id && (

            <div
              className="claim-box"
              style={{
                marginTop: "24px",
              }}
            >

              <h2>
              📩 Contact Finder
              </h2>


  <p>
  Did you lose this item?
  Send a message to the person who found it.
  Please include your contact number in the message
  so the finder can contact you directly.
</p>


              {/* ----------------------------------------------
                  CONTACT BUTTON
              ---------------------------------------------- */}

              {!contactOpen && (

                <button
                  type="button"
                  className="primary-btn full"
                  onClick={() => {

                    setContactOpen(true);

                    setContactSuccess("");

                    setContactError("");

                  }}
                >
                  📧 Contact Owner
                </button>

              )}


              {/* ----------------------------------------------
                  CONTACT FORM
              ---------------------------------------------- */}

              {contactOpen && (

                <form
                  onSubmit={contactOwner}
                  className="claim-form"
                >


                  {/* SUCCESS */}

                  {contactSuccess && (

                    <div className="success-box">
                      ✓ {contactSuccess}
                    </div>

                  )}


                  {/* ERROR */}

                  {contactError && (

                    <div className="error-box">
                      {contactError}
                    </div>

                  )}


                  {/* MESSAGE */}

                  <label>
                    Your Message
                  </label>


                  <textarea
                    value={contactMessage}
                    onChange={(e) =>
                      setContactMessage(
                        e.target.value
                      )
                    }
                    placeholder="Example: I think this is my wallet. It contains my college ID and has a small scratch on the left side..."
                    required
                  />


                  {/* SEND */}

                  <button
                    type="submit"
                    className="primary-btn full"
                    disabled={
                      contactLoading
                    }
                  >

                    {contactLoading
  ? "📩 Sending..."
  : "📩 Send Message"}
                  </button>


                  {/* CANCEL */}

                  <button
                    type="button"
                    className="secondary-btn full"
                    style={{
                      marginTop: "10px",
                    }}
                    onClick={() => {

                      setContactOpen(false);

                      setContactMessage("");

                      setContactError("");

                      setContactSuccess("");

                    }}
                  >
                    Cancel
                  </button>

                </form>

              )}

            </div>

          )}


          {/* ==================================================
              AI MATCHING
          ================================================== */}

          {(
            user?.role === "admin" ||
            user?.id === item.user_id
          ) && (

            <div
              className="claim-box"
              style={{
                marginTop: "24px",
              }}
            >

              <h2>
                🤖 AI Possible Matches
              </h2>


              <p>
                Find verified opposite-type
                items with similar images
                using CLIP AI.
              </p>


              {/* AI MESSAGE */}

              {aiMessage && (

                <div className="success-box">
                  {aiMessage}
                </div>

              )}


              {/* AI ERROR */}

              {aiError && (

                <div className="error-box">
                  {aiError}
                </div>

              )}


              {/* RUN AI */}

              <button
                type="button"
                className="primary-btn full"
                onClick={runAIMatching}
                disabled={aiLoading}
              >

                {aiLoading
                  ? "🤖 AI is matching..."
                  : "🤖 Run AI Match"}

              </button>


              {/* AI RESULTS */}

              {aiMatches.length > 0 && (

                <div
                  style={{
                    marginTop: "20px",
                  }}
                >

                  <h3>
                    Possible Matches (
                    {aiMatches.length}
                    )
                  </h3>


                  {aiMatches.map(
                    (match) => (

                      <Link
                        key={
                          `${match.item_id}-${match.matched_item_id}`
                        }
                        to={
                          `/items/${match.matched_item_id}`
                        }
                        style={{
                          display: "block",
                          textDecoration: "none",
                          color: "inherit",
                          padding: "14px",
                          marginTop: "12px",
                          border:
                            "1px solid #e5e7eb",
                          borderRadius: "10px",
                        }}
                      >

                        <strong>
                          {match.matched_title}
                        </strong>


                        <div
                          style={{
                            marginTop: "5px",
                          }}
                        >

                          {match.matched_type ===
                          "lost"

                            ? "🔴 LOST"

                            : "🟢 FOUND"}

                          {" · "}

                          Item #
                          {match.matched_item_id}

                        </div>


                        <div
                          style={{
                            marginTop: "8px",
                            fontWeight: "700",
                          }}
                        >

                          🤖 Similarity:{" "}

                          {
                            match.similarity_percentage
                          }%

                        </div>

                      </Link>

                    )
                  )}

                </div>

              )}


              {/* NO MATCH */}

              {!aiLoading &&
                aiMessage &&
                aiMatches.length === 0 &&
                !aiError && (

                  <p
                    style={{
                      marginTop: "12px",
                    }}
                  >
                    No possible matches were
                    found above the current
                    similarity threshold.
                  </p>

                )}

            </div>

          )}


          {/* ==================================================
              CLAIM
          ================================================== */}

          {user ? (

            <div
              className="claim-box"
              style={{
                marginTop: "24px",
              }}
            >

              <h2>
                Is this your item?
              </h2>


              <p>
                Provide details that can
                help verify your ownership.
              </p>


              {/* CLAIM SUCCESS */}

              {message && (

                <div className="success-box">
                  {message}
                </div>

              )}


              {/* CLAIM ERROR */}

              {error && (

                <div className="error-box">
                  {error}
                </div>

              )}


              <form
                onSubmit={submitClaim}
                className="claim-form"
              >

                <textarea
                  placeholder="Example: This wallet contains my college ID, a family photo and has a scratch on the left corner..."
                  value={proof}
                  onChange={(e) =>
                    setProof(
                      e.target.value
                    )
                  }
                  required
                />


                <button
                  className="primary-btn full"
                  disabled={
                    claimLoading
                  }
                >

                  {claimLoading
                    ? "Submitting..."
                    : "🤝 Submit Claim"}

                </button>

              </form>

            </div>

          ) : (

            <div
              className="login-claim-box"
              style={{
                marginTop: "24px",
              }}
            >

              <h2>
                Think this is yours?
              </h2>


              <p>
                Login to submit a claim
                with proof of ownership.
              </p>


              <Link
                to="/login"
                className="primary-btn"
              >
                Login to Claim
              </Link>

            </div>

          )}

        </div>

      </div>

    </div>

  );
}
// ============================================================
// MY CLAIMS
// ============================================================

function MyClaims({ user }) {

  const [claims, setClaims] =
    useState([]);

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {

    if (!user) {

      setLoading(false);

      return;
    }


    const loadClaims = async () => {

      try {

        const response =
          await API.get(
            "/api/claims/my"
          );

        setClaims(
          response.data
        );

      } catch (error) {

        console.error(error);

      } finally {

        setLoading(false);

      }
    };


    loadClaims();

  }, [user]);


  if (!user) {

    return (

      <div className="auth-required">

        <h2>
          Login required
        </h2>


        <Link
          to="/login"
          className="primary-btn"
        >
          Login
        </Link>

      </div>

    );
  }


  return (

    <div className="page-container">

      <span className="section-label">
        CLAIM HISTORY
      </span>


      <h1>
        My Claims
      </h1>


      {loading ? (

        <div className="empty-state">
          Loading...
        </div>

      ) : claims.length === 0 ? (

        <div className="empty-state">

          <div className="empty-icon">
            🤝
          </div>


          <h3>
            No claims yet
          </h3>


          <p>
            Your submitted claims will
            appear here.
          </p>

        </div>

      ) : (

        <div className="claims-list">

          {claims.map(
            (claim) => (

              <div
                key={claim.id}
                className="claim-history-card"
              >

                <div>

                  <span className="claim-id">
                    CLAIM #{claim.id}
                  </span>


                  <h3>
                    Item #{claim.item_id}
                  </h3>


                  <p>
                    {claim.proof}
                  </p>

                </div>


                <span
                  className={
                    `claim-status ${claim.status}`
                  }
                >
                  {claim.status}
                </span>

              </div>

            )
          )}

        </div>

      )}

    </div>
  );
}


// ============================================================
// LOGIN
// ============================================================

function Login({ setUser }) {

  const navigate =
    useNavigate();


  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  const login = async (e) => {

    e.preventDefault();

    setError("");


    try {

      setLoading(true);


      const response =
        await API.post(
          "/api/auth/login",
          {
            email,
            password,
          }
        );


      const token =
        response.data.access_token;


      const user =
        response.data.user;


      localStorage.setItem(
        "refindx_token",
        token
      );


      localStorage.setItem(
        "refindx_user",
        JSON.stringify(user)
      );


      setUser(user);

      navigate("/");

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Login failed"
      );

    } finally {

      setLoading(false);

    }
  };


  return (

    <AuthLayout
      title="Welcome back"
      subtitle="Login to your ReFindX account"
    >

      <form
        onSubmit={login}
        className="auth-form"
      >

        {error && (

          <div className="error-box">
            {error}
          </div>

        )}


        <label>
          Email
        </label>


        <input
          type="email"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
          required
        />


        <label>
          Password
        </label>


        <input
          type="password"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
          required
        />


        <button
          className="primary-btn full"
          disabled={loading}
        >

          {loading
            ? "Logging in..."
            : "Login"}

        </button>

      </form>


      <p className="auth-footer">

        Don't have an account?

        <Link to="/signup">
          Create account
        </Link>

      </p>

    </AuthLayout>
  );
}
// ============================================================
// SIGNUP
// ============================================================

function Signup({ setUser }) {

  const navigate = useNavigate();


  // ==========================================================
  // SIGNUP FIELDS
  // ==========================================================

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");


  // ==========================================================
  // OTP
  // ==========================================================

  const [otp, setOtp] =
    useState("");

  const [otpMode, setOtpMode] =
    useState(false);


  // ==========================================================
  // UI STATES
  // ==========================================================

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [resendLoading, setResendLoading] =
    useState(false);


  // ==========================================================
  // OTP COUNTDOWN
  // ==========================================================

  const [secondsLeft, setSecondsLeft] =
    useState(0);


  // ==========================================================
  // COUNTDOWN
  // ==========================================================

  useEffect(() => {

    if (!otpMode || secondsLeft <= 0) {
      return;
    }


    const timer = setInterval(() => {

      setSecondsLeft(
        (previous) => previous - 1
      );

    }, 1000);


    return () => {
      clearInterval(timer);
    };

  }, [otpMode, secondsLeft]);


  // ==========================================================
  // FORMAT TIMER
  // ==========================================================

  const formatTime = () => {

    const minutes =
      Math.floor(secondsLeft / 60);

    const seconds =
      secondsLeft % 60;

    return `${minutes}:${String(seconds).padStart(2, "0")}`;
  };


  // ==========================================================
  // SIGNUP
  // ==========================================================

  const signup = async (e) => {

    e.preventDefault();

    setError("");
    setSuccess("");


    if (!name.trim()) {

      setError(
        "Please enter your name."
      );

      return;
    }


    if (!email.trim()) {

      setError(
        "Please enter your email."
      );

      return;
    }


    if (password.length < 8) {

      setError(
        "Password must be at least 8 characters."
      );

      return;
    }


    try {

      setLoading(true);


      const response =
        await API.post(
          "/api/auth/signup",
          {
            name: name.trim(),
            email: email.trim(),
            password,
          }
        );


      // ------------------------------------------------------
      // OTP REQUIRED
      // ------------------------------------------------------

      if (
        response.data.requires_verification
      ) {

        setOtpMode(true);

        setSuccess(
          response.data.message ||
          "OTP sent to your email."
        );

        // 5 minutes
        setSecondsLeft(300);

      } else {

        navigate("/login");

      }


    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Signup failed."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==========================================================
  // VERIFY OTP
  // ==========================================================

  const verifyOTP = async (e) => {

    e.preventDefault();

    setError("");
    setSuccess("");


    if (!otp.trim()) {

      setError(
        "Please enter the OTP."
      );

      return;
    }


    if (otp.trim().length !== 6) {

      setError(
        "OTP must contain 6 digits."
      );

      return;
    }


    try {

      setLoading(true);


      const response =
        await API.post(
          "/api/auth/verify-email",
          {
            email: email.trim(),
            otp: otp.trim(),
          }
        );


      // ------------------------------------------------------
      // SAVE LOGIN
      // ------------------------------------------------------

      localStorage.setItem(
        "refindx_token",
        response.data.access_token
      );


      localStorage.setItem(
        "refindx_user",
        JSON.stringify(
          response.data.user
        )
      );


      setUser(
        response.data.user
      );


      setSuccess(
        "Email verified successfully! 🎉"
      );


      // ------------------------------------------------------
      // GO HOME
      // ------------------------------------------------------

      setTimeout(() => {

        navigate("/");

      }, 1000);


    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Invalid or expired OTP."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==========================================================
  // RESEND OTP
  // ==========================================================

  const resendOTP = async () => {

    setError("");
    setSuccess("");


    try {

      setResendLoading(true);


      const response =
        await API.post(
          "/api/auth/resend-otp",
          {
            email: email.trim(),
          }
        );


      setSuccess(
        response.data.message ||
        "A new OTP has been sent."
      );


      // Reset 5 minute timer

      setSecondsLeft(300);


      setOtp("");


    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not resend OTP."
      );

    } finally {

      setResendLoading(false);

    }
  };


  // ==========================================================
  // OTP SCREEN
  // ==========================================================

  if (otpMode) {

    return (

      <AuthLayout
        title="Verify Your Email"
        subtitle={
          `Enter the 6-digit OTP sent to ${email}`
        }
      >

        <form
          onSubmit={verifyOTP}
          className="auth-form"
        >

          {/* SUCCESS */}

          {success && (

            <div className="success-box">

              {success}

            </div>

          )}


          {/* ERROR */}

          {error && (

            <div className="error-box">

              {error}

            </div>

          )}


          <label>
            Verification OTP
          </label>


          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={otp}
            onChange={(e) => {

              const value =
                e.target.value.replace(
                  /\D/g,
                  ""
                );

              setOtp(value);

            }}
            placeholder="Enter 6-digit OTP"
            autoComplete="one-time-code"
            required
          />


          {/* TIMER */}

          {secondsLeft > 0 ? (

            <p
              style={{
                textAlign: "center",
                margin: "10px 0",
                color: "#666",
              }}
            >

              OTP expires in{" "}

              <strong>
                {formatTime()}
              </strong>

            </p>

          ) : (

            <p
              style={{
                textAlign: "center",
                margin: "10px 0",
                color: "#d9534f",
              }}
            >

              OTP expired. Please resend OTP.

            </p>

          )}


          {/* VERIFY BUTTON */}

          <button
            type="submit"
            className="primary-btn full"
            disabled={
              loading ||
              otp.length !== 6
            }
          >

            {loading
              ? "Verifying..."
              : "Verify Email"}

          </button>


          {/* RESEND */}

          <button
            type="button"
            className="secondary-btn full"
            onClick={resendOTP}
            disabled={
              resendLoading ||
              secondsLeft > 0
            }
            style={{
              marginTop: "10px",
            }}
          >

            {resendLoading
              ? "Sending..."
              : secondsLeft > 0
                ? `Resend OTP in ${formatTime()}`
                : "Resend OTP"}

          </button>


          {/* BACK */}

          <button
            type="button"
            onClick={() => {

              setOtpMode(false);
              setOtp("");
              setError("");
              setSuccess("");

            }}
            style={{
              width: "100%",
              marginTop: "10px",
              background: "transparent",
              border: "none",
              cursor: "pointer",
            }}
          >

            ← Back to Signup

          </button>

        </form>

      </AuthLayout>
    );
  }


  // ==========================================================
  // SIGNUP SCREEN
  // ==========================================================

  return (

    <AuthLayout
      title="Join ReFindX"
      subtitle="Create an account and help reunite lost items"
    >

      <form
        onSubmit={signup}
        className="auth-form"
      >

        {/* ERROR */}

        {error && (

          <div className="error-box">

            {error}

          </div>

        )}


        <label>
          Name
        </label>


        <input
          value={name}
          onChange={(e) =>
            setName(
              e.target.value
            )
          }
          required
        />


        <label>
          Email
        </label>


        <input
          type="email"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
          required
        />


        <label>
          Password
        </label>


        <input
          type="password"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
          required
        />


        <button
          type="submit"
          className="primary-btn full"
          disabled={loading}
        >

          {loading
            ? "Creating..."
            : "Create Account"}

        </button>

      </form>

    </AuthLayout>
  );
}

// ============================================================
// AUTH LAYOUT
// ============================================================

function AuthLayout({
  title,
  subtitle,
  children,
}) {

  return (

    <div className="auth-page">

      <div className="auth-card">

        <div className="auth-logo">

          <span>
            R
          </span>

          ReFindX

        </div>


        <h1>
          {title}
        </h1>


        <p>
          {subtitle}
        </p>


        {children}

      </div>

    </div>
  );
}


// ============================================================
// REPORT ITEM
// ============================================================

function ReportItem({ user }) {

  const [form, setForm] =
    useState({
      type: "lost",
      title: "",
      category: "",
      description: "",
      location: "",
      date_lost_found: "",
    });


  const [image, setImage] =
    useState(null);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  if (!user) {

    return (

      <div className="auth-required">

        <h2>
          Login required
        </h2>


        <p>
          Please login before reporting
          a lost or found item.
        </p>


        <Link
          to="/login"
          className="primary-btn"
        >
          Login
        </Link>

      </div>

    );
  }


  const submit = async (e) => {

    e.preventDefault();

    setError("");
    setMessage("");


    if (!image) {

      setError(
        "Please select an image."
      );

      return;
    }


    try {

      setLoading(true);


      const data =
        new FormData();


      Object.entries(form).forEach(
        ([key, value]) => {

          data.append(
            key,
            value
          );

        }
      );


      data.append(
        "image",
        image
      );


      const response =
        await API.post(
          "/api/items/create",
          data,
          {
            headers: {
              "Content-Type":
                "multipart/form-data",
            },
          }
        );


      setMessage(
        response.data.message +
        " Waiting for admin verification."
      );


      setForm({
        type: "lost",
        title: "",
        category: "",
        description: "",
        location: "",
        date_lost_found: "",
      });


      setImage(null);

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not submit item."
      );

    } finally {

      setLoading(false);

    }
  };


  return (

    <div className="form-page">

      <div className="form-header">

        <span className="section-label">
          REPORT ITEM
        </span>


        <h1>
          Help someone find it.
        </h1>


        <p>
          Submit accurate information and
          a clear photo. Our team will verify
          it before publishing.
        </p>

      </div>


      <form
        onSubmit={submit}
        className="item-form"
      >

        {message && (

          <div className="success-box">
            {message}
          </div>

        )}


        {error && (

          <div className="error-box">
            {error}
          </div>

        )}


        <div className="type-toggle">

          <button
            type="button"
            className={
              form.type === "lost"
                ? "selected"
                : ""
            }
            onClick={() =>
              setForm({
                ...form,
                type: "lost",
              })
            }
          >
            🔴 I Lost an Item
          </button>


          <button
            type="button"
            className={
              form.type === "found"
                ? "selected"
                : ""
            }
            onClick={() =>
              setForm({
                ...form,
                type: "found",
              })
            }
          >
            🟢 I Found an Item
          </button>

        </div>


        <label>
          Item title
        </label>


        <input
          placeholder="e.g. Black leather wallet"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
        />


        <label>
          Category
        </label>


        <input
          placeholder="Wallet, Phone, ID Card..."
          value={form.category}
          onChange={(e) =>
            setForm({
              ...form,
              category: e.target.value,
            })
          }
          required
        />


        <label>
          Description
        </label>


        <textarea
          placeholder="Describe identifying features..."
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description:
                e.target.value,
            })
          }
          required
        />


        <label>
          Location
        </label>


        <input
          placeholder="Where was it lost/found?"
          value={form.location}
          onChange={(e) =>
            setForm({
              ...form,
              location:
                e.target.value,
            })
          }
          required
        />


        <label>
          Date
        </label>


        <input
          type="date"
          value={
            form.date_lost_found
          }
          onChange={(e) =>
            setForm({
              ...form,
              date_lost_found:
                e.target.value,
            })
          }
          required
        />


        <label>
          Item photo
        </label>


        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) =>
            setImage(
              e.target.files[0]
            )
          }
          required
        />


        <button
          className="primary-btn full"
          disabled={loading}
        >

          {loading
            ? "Submitting..."
            : "Submit Item"}

        </button>

      </form>

    </div>
  );
}


// ============================================================
// NOTIFICATIONS
// ============================================================

function Notifications() {

  const navigate = useNavigate();

  const [notifications, setNotifications] =
    useState([]);

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {

    const load = async () => {

      try {

        setLoading(true);

        const response =
          await API.get(
            "/api/notifications/"
          );

        setNotifications(
          response.data
        );

      } catch (error) {

        console.error(
          "Notification loading error:",
          error
        );

      } finally {

        setLoading(false);

      }

    };


    load();

  }, []);


  const openNotification = async (
    notification
  ) => {

    try {

      if (!notification.is_read) {

        await API.patch(
          `/api/notifications/${notification.id}/read`
        );

      }

    } catch (error) {

      console.error(
        "Could not mark notification as read:",
        error
      );

    }


    if (notification.item_id) {

      navigate(
        `/items/${notification.item_id}`
      );

      return;
    }

  };


  if (loading) {

    return (

      <div className="page-container">

        <span className="section-label">
          NOTIFICATIONS
        </span>

        <h1>
          Your updates
        </h1>

        <div className="empty-state">
          Loading notifications...
        </div>

      </div>

    );

  }


  return (

    <div className="page-container">

      <span className="section-label">
        NOTIFICATIONS
      </span>

      <h1>
        Your updates
      </h1>


      {notifications.length === 0 ? (

        <div className="empty-state">

          <div className="empty-icon">
            🔔
          </div>

          <h3>
            No notifications
          </h3>

          <p>
            You're all caught up.
          </p>

        </div>

      ) : (

        <div className="notification-list">

          {notifications.map(
            (notification) => (

              <div
                key={notification.id}

                className={
                  notification.is_read
                    ? "notification read"
                    : "notification unread"
                }

                onClick={() =>
                  openNotification(
                    notification
                  )
                }

                style={{
                  cursor:
                    notification.item_id
                      ? "pointer"
                      : "default",
                }}
              >

                <div className="notification-icon">

                  {notification.item_id
                    ? "🤖"
                    : "🔔"}

                </div>


                <div
                  style={{
                    flex: 1,
                  }}
                >

                  <p>
                    {notification.message}
                  </p>


                  {notification.item_id && (

                    <span
                      style={{
                        display:
                          "inline-block",

                        marginTop:
                          "6px",

                        fontSize:
                          "13px",

                        fontWeight:
                          "600",
                      }}
                    >
                      View related item →
                    </span>

                  )}


                  {!notification.is_read && (

                    <span
                      className="new-badge"
                    >
                      NEW
                    </span>

                  )}

                </div>

              </div>

            )
          )}

        </div>

      )}

    </div>
  );
}


// ============================================================
// ADMIN DASHBOARD
// ============================================================

function AdminDashboard({ user }) {

  const [pendingItems, setPendingItems] =
    useState([]);

  const [pendingClaims, setPendingClaims] =
    useState([]);

  const [stats, setStats] =
    useState({
      total_users: 0,
      total_items: 0,
      pending_items: 0,
      total_claims: 0,
      pending_claims: 0,
      ai_matches: 0,
      successful_returns: 0,
      lost_items: 0,
      found_items: 0,
      verified_items: 0,
      rejected_items: 0,
      approved_claims: 0,
      rejected_claims: 0,
    });


  const [loading, setLoading] =
    useState(true);

  const [actionLoading, setActionLoading] =
    useState(null);

  const [aiLoading, setAiLoading] =
    useState(null);

  const [aiResults, setAiResults] =
    useState({});

  const [aiErrors, setAiErrors] =
    useState({});

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");


  // ==========================================================
  // LOAD ADMIN DATA + STATS
  // ==========================================================

  const loadAdminData = async () => {

    try {

      setLoading(true);

      setError("");


      const [
        statsResponse,
        itemsResponse,
        claimsResponse,
      ] = await Promise.all([

        API.get(
          "/api/admin/stats"
        ),

        API.get(
          "/api/admin/items/pending"
        ),

        API.get(
          "/api/admin/claims/pending"
        ),

      ]);


      setStats(
        statsResponse.data
      );


      setPendingItems(
        itemsResponse.data
      );


      setPendingClaims(
        claimsResponse.data
      );

    } catch (error) {

      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Could not load admin dashboard."
      );

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {

    if (
      user?.role === "admin"
    ) {

      loadAdminData();

    }

  }, [user]);


  // ==========================================================
  // VERIFY ITEM
  // ==========================================================

  const verifyItem = async (
    itemId
  ) => {

    try {

      setActionLoading(
        `verify-item-${itemId}`
      );

      setMessage("");
      setError("");


      await API.patch(
        `/api/admin/items/${itemId}/verify`
      );


      setMessage(
        `Item #${itemId} verified successfully.`
      );


      setPendingItems(
        (previous) =>
          previous.filter(
            (item) =>
              item.id !== itemId
          )
      );


      await loadAdminData();

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not verify item."
      );

    } finally {

      setActionLoading(null);

    }
  };


  // ==========================================================
  // REJECT ITEM
  // ==========================================================

  const rejectItem = async (
    itemId
  ) => {

    try {

      setActionLoading(
        `reject-item-${itemId}`
      );

      setMessage("");
      setError("");


      await API.patch(
        `/api/admin/items/${itemId}/reject`
      );


      setMessage(
        `Item #${itemId} rejected.`
      );


      setPendingItems(
        (previous) =>
          previous.filter(
            (item) =>
              item.id !== itemId
          )
      );


      await loadAdminData();

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not reject item."
      );

    } finally {

      setActionLoading(null);

    }
  };


  // ==========================================================
  // DELETE ITEM
  // ==========================================================

  const deleteItem = async (
    itemId,
    title
  ) => {

    const confirmed =
      window.confirm(
        `Delete "${title}" permanently?`
      );


    if (!confirmed) {
      return;
    }


    try {

      setActionLoading(
        `delete-item-${itemId}`
      );

      setMessage("");
      setError("");


      await API.delete(
        `/api/admin/items/${itemId}`
      );


      setMessage(
        `Item #${itemId} deleted successfully.`
      );


      setPendingItems(
        (previous) =>
          previous.filter(
            (item) =>
              item.id !== itemId
          )
      );


      await loadAdminData();

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not delete item."
      );

    } finally {

      setActionLoading(null);

    }
  };


  // ==========================================================
  // APPROVE CLAIM
  // ==========================================================

  const approveClaim = async (
    claimId
  ) => {

    try {

      setActionLoading(
        `approve-claim-${claimId}`
      );

      setMessage("");
      setError("");


      await API.patch(
        `/api/admin/claims/${claimId}/approve`
      );


      setMessage(
        `Claim #${claimId} approved successfully.`
      );


      setPendingClaims(
        (previous) =>
          previous.filter(
            (claim) =>
              claim.id !== claimId
          )
      );


      await loadAdminData();

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not approve claim."
      );

    } finally {

      setActionLoading(null);

    }
  };


  // ==========================================================
  // REJECT CLAIM
  // ==========================================================

  const rejectClaim = async (
    claimId
  ) => {

    try {

      setActionLoading(
        `reject-claim-${claimId}`
      );

      setMessage("");
      setError("");


      await API.patch(
        `/api/admin/claims/${claimId}/reject`
      );


      setMessage(
        `Claim #${claimId} rejected.`
      );


      setPendingClaims(
        (previous) =>
          previous.filter(
            (claim) =>
              claim.id !== claimId
          )
      );


      await loadAdminData();

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Could not reject claim."
      );

    } finally {

      setActionLoading(null);

    }
  };


  // ==========================================================
  // RUN AI MATCHING
  // ==========================================================

  const runAIMatch = async (
    itemId
  ) => {

    try {

      setAiLoading(itemId);


      setAiErrors(
        (previous) => ({
          ...previous,
          [itemId]: "",
        })
      );


      const response =
        await API.post(
          `/api/ai/match/${itemId}`
        );


      setAiResults(
        (previous) => ({
          ...previous,
          [itemId]:
            response.data,
        })
      );


      await loadAdminData();

    } catch (error) {

      console.error(error);


      setAiErrors(
        (previous) => ({
          ...previous,
          [itemId]:
            error.response?.data?.detail ||
            "Could not run AI matching.",
        })
      );

    } finally {

      setAiLoading(null);

    }
  };


  // ==========================================================
  // ACCESS CONTROL
  // ==========================================================

  if (
    user?.role !== "admin"
  ) {

    return (

      <div className="auth-required">

        <div>

          <h2>
            🛡️ Admin access required
          </h2>


          <p>
            You do not have permission
            to access this dashboard.
          </p>


          <Link
            to="/"
            className="primary-btn"
          >
            Back to Home
          </Link>

        </div>

      </div>

    );
  }


  // ==========================================================
  // DASHBOARD
  // ==========================================================

  return (

    <div className="admin-page">

      {/* ====================================================
          HEADER
      ==================================================== */}

      <div className="admin-header">

        <div>

          <span className="section-label">
            ADMIN CONTROL CENTER
          </span>


          <h1>
            ReFindX Dashboard
          </h1>


          <p>
            Monitor users, items, claims,
            AI matches and successful returns.
          </p>

        </div>


        <button
          className="refresh-btn"
          onClick={loadAdminData}
          disabled={loading}
        >

          {loading
            ? "↻ Loading..."
            : "↻ Refresh"}

        </button>

      </div>


      {message && (

        <div className="success-box admin-message">
          ✓ {message}
        </div>

      )}


      {error && (

        <div className="error-box admin-message">
          {error}
        </div>

      )}


      {/* ====================================================
          MAIN STATISTICS
      ==================================================== */}

      <section
        style={{
          marginBottom: "35px",
        }}
      >

        <div
          style={{
            marginBottom: "18px",
          }}
        >

          <span className="section-label">
            PLATFORM OVERVIEW
          </span>


          <h2>
            Dashboard Statistics
          </h2>

        </div>


        <div className="admin-stats">

          {/* TOTAL USERS */}

          <div className="stat-card">

            <span>
              👥 TOTAL USERS
            </span>


            <strong>
              {stats.total_users}
            </strong>


            <small>
              Registered users
            </small>

          </div>


          {/* TOTAL ITEMS */}

          <div className="stat-card">

            <span>
              📦 TOTAL ITEMS
            </span>


            <strong>
              {stats.total_items}
            </strong>


            <small>
              All reported items
            </small>

          </div>


          {/* PENDING ITEMS */}

          <div className="stat-card">

            <span>
              ⏳ PENDING ITEMS
            </span>


            <strong>
              {stats.pending_items}
            </strong>


            <small>
              Awaiting verification
            </small>

          </div>


          {/* TOTAL CLAIMS */}

          <div className="stat-card">

            <span>
              🤝 TOTAL CLAIMS
            </span>


            <strong>
              {stats.total_claims}
            </strong>


            <small>
              Submitted claims
            </small>

          </div>


          {/* PENDING CLAIMS */}

          <div className="stat-card">

            <span>
              ⏳ PENDING CLAIMS
            </span>


            <strong>
              {stats.pending_claims}
            </strong>


            <small>
              Awaiting review
            </small>

          </div>


          {/* AI MATCHES */}

          <div className="stat-card">

            <span>
              🤖 AI MATCHES
            </span>


            <strong>
              {stats.ai_matches}
            </strong>


            <small>
              CLIP matches generated
            </small>

          </div>


          {/* SUCCESSFUL RETURNS */}

          <div className="stat-card">

            <span>
              🎉 SUCCESSFUL RETURNS
            </span>


            <strong>
              {stats.successful_returns}
            </strong>


            <small>
              Successfully claimed items
            </small>

          </div>

        </div>

      </section>


      {/* ====================================================
          ITEM STATISTICS
      ==================================================== */}

      <section
        style={{
          marginBottom: "35px",
        }}
      >

        <div
          style={{
            marginBottom: "18px",
          }}
        >

          <span className="section-label">
            ITEM ANALYTICS
          </span>


          <h2>
            Item Overview
          </h2>

        </div>


        <div className="admin-stats">

          <div className="stat-card">

            <span>
              🔴 LOST ITEMS
            </span>


            <strong>
              {stats.lost_items}
            </strong>


            <small>
              Lost reports
            </small>

          </div>


          <div className="stat-card">

            <span>
              🟢 FOUND ITEMS
            </span>


            <strong>
              {stats.found_items}
            </strong>


            <small>
              Found reports
            </small>

          </div>


          <div className="stat-card">

            <span>
              ✓ VERIFIED ITEMS
            </span>


            <strong>
              {stats.verified_items}
            </strong>


            <small>
              Admin verified
            </small>

          </div>


          <div className="stat-card">

            <span>
              ✕ REJECTED ITEMS
            </span>


            <strong>
              {stats.rejected_items}
            </strong>


            <small>
              Rejected reports
            </small>

          </div>

        </div>

      </section>


      {/* ====================================================
          CLAIM STATISTICS
      ==================================================== */}

      <section
        style={{
          marginBottom: "35px",
        }}
      >

        <div
          style={{
            marginBottom: "18px",
          }}
        >

          <span className="section-label">
            CLAIM ANALYTICS
          </span>


          <h2>
            Claim Overview
          </h2>

        </div>


        <div className="admin-stats">

          <div className="stat-card">

            <span>
              ✓ APPROVED CLAIMS
            </span>


            <strong>
              {stats.approved_claims}
            </strong>


            <small>
              Successfully approved
            </small>

          </div>


          <div className="stat-card">

            <span>
              ✕ REJECTED CLAIMS
            </span>


            <strong>
              {stats.rejected_claims}
            </strong>


            <small>
              Rejected requests
            </small>

          </div>

        </div>

      </section>


      {/* ====================================================
          PENDING ITEMS
      ==================================================== */}

      <section className="admin-section">

        <div className="admin-section-header">

          <div>

            <span className="section-label">
              MODERATION
            </span>


            <h2>
              Pending Items
            </h2>

          </div>


          <span className="count-pill">
            {pendingItems.length}
          </span>

        </div>


        {loading ? (

          <div className="admin-empty">
            Loading pending items...
          </div>

        ) : pendingItems.length === 0 ? (

          <div className="admin-empty">

            <div className="empty-icon">
              ✓
            </div>


            <h3>
              All caught up
            </h3>


            <p>
              There are no items waiting
              for verification.
            </p>

          </div>

        ) : (

          <div className="admin-item-list">

            {pendingItems.map(
              (item) => {

                const imageUrl =
                  item.image_url
                    ? `https://refindx.onrender.com${item.image_url}`
                    : null;


                return (

                  <div
                    key={item.id}
                    className="admin-item-card"
                  >

                    <div className="admin-item-image">

                      {imageUrl ? (

                        <img
                          src={imageUrl}
                          alt={item.title}
                        />

                      ) : (

                        <div className="no-image">
                          No Image
                        </div>

                      )}

                    </div>


                    <div className="admin-item-info">

                      <div className="admin-item-top">

                        <span
                          className={
                            item.type === "lost"
                              ? "status lost"
                              : "status found"
                          }
                        >
                          {item.type}
                        </span>


                        <span className="item-id">
                          #{item.id}
                        </span>

                      </div>


                      <h3>
                        {item.title}
                      </h3>


                      <p>
                        {item.description}
                      </p>


                      <div className="admin-meta">

                        <span>
                          📁 {item.category}
                        </span>


                        <span>
                          📍 {item.location}
                        </span>


                        <span>
                          📅 {item.date_lost_found}
                        </span>

                      </div>


                      <div className="admin-actions">

                        <button
                          className="approve-btn"
                          disabled={
                            actionLoading ===
                            `verify-item-${item.id}`
                          }
                          onClick={() =>
                            verifyItem(
                              item.id
                            )
                          }
                        >

                          {actionLoading ===
                          `verify-item-${item.id}`
                            ? "Verifying..."
                            : "✓ Verify"}

                        </button>


                        <button
                          className="reject-btn"
                          disabled={
                            actionLoading ===
                            `reject-item-${item.id}`
                          }
                          onClick={() =>
                            rejectItem(
                              item.id
                            )
                          }
                        >

                          {actionLoading ===
                          `reject-item-${item.id}`
                            ? "Rejecting..."
                            : "✕ Reject"}

                        </button>


                        <button
                          className="reject-btn"
                          disabled={
                            actionLoading ===
                            `delete-item-${item.id}`
                          }
                          onClick={() =>
                            deleteItem(
                              item.id,
                              item.title
                            )
                          }
                        >

                          {actionLoading ===
                          `delete-item-${item.id}`
                            ? "Deleting..."
                            : "🗑️ Delete"}

                        </button>


                        <button
                          type="button"
                          className="primary-btn"
                          disabled={
                            aiLoading === item.id
                          }
                          onClick={() =>
                            runAIMatch(
                              item.id
                            )
                          }
                        >

                          {aiLoading === item.id
                            ? "🤖 Matching..."
                            : "🤖 AI Match"}

                        </button>

                      </div>


                      {aiErrors[item.id] && (

                        <div className="error-box">

                          {aiErrors[item.id]}

                        </div>

                      )}


                      {aiResults[item.id] && (

                        <div
                          className="success-box"
                          style={{
                            marginTop: "12px",
                          }}
                        >

                          <strong>
                            🤖 AI Matching Complete
                          </strong>


                          <div
                            style={{
                              marginTop: "8px",
                            }}
                          >

                            {aiResults[item.id]
                              .matches_found === 0

                              ? "No possible matches found."

                              : `${aiResults[item.id].matches_found} possible match(es) found.`}

                          </div>


                          {aiResults[item.id]
                            .matches
                            ?.map(
                              (match) => (

                                <Link
                                  key={
                                    `${match.item_id}-${match.matched_item_id}`
                                  }
                                  to={
                                    `/items/${match.matched_item_id}`
                                  }
                                  style={{
                                    display:
                                      "block",

                                    marginTop:
                                      "10px",

                                    textDecoration:
                                      "none",

                                    color:
                                      "inherit",
                                  }}
                                >

                                  <strong>
                                    {match.matched_title}
                                  </strong>

                                  {" · "}

                                  Item #
                                  {match.matched_item_id}

                                  {" · "}

                                  🤖{" "}
                                  {match.similarity_percentage}%

                                </Link>

                              )
                            )}

                        </div>

                      )}

                    </div>

                  </div>

                );

              }
            )}

          </div>

        )}

      </section>


      {/* ====================================================
          PENDING CLAIMS
      ==================================================== */}

      <section className="admin-section">

        <div className="admin-section-header">

          <div>

            <span className="section-label">
              CLAIM REVIEW
            </span>


            <h2>
              Pending Claims
            </h2>

          </div>


          <span className="count-pill">
            {pendingClaims.length}
          </span>

        </div>


        {loading ? (

          <div className="admin-empty">
            Loading pending claims...
          </div>

        ) : pendingClaims.length === 0 ? (

          <div className="admin-empty">

            <div className="empty-icon">
              ✓
            </div>


            <h3>
              No pending claims
            </h3>


            <p>
              Claim requests will appear here.
            </p>

          </div>

        ) : (

          <div className="admin-claims-list">

            {pendingClaims.map(
              (claim) => (

                <div
                  key={claim.id}
                  className="admin-claim-card"
                >

                  <div className="claim-main">

                    <div className="claim-heading">

                      <span className="claim-id">
                        CLAIM #{claim.id}
                      </span>


                      <span className="pending-badge">
                        PENDING
                      </span>

                    </div>


                    <h3>
                      Item #{claim.item_id}
                    </h3>


                    <p className="claim-proof">
                      "{claim.proof}"
                    </p>


                    <div className="claim-meta">

                      <span>
                        Claimant ID:{" "}
                        {claim.claimant_id}
                      </span>


                      <span>
                        Created:{" "}

                        {claim.created_at
                          ? new Date(
                              claim.created_at
                            ).toLocaleString()
                          : "—"}

                      </span>

                    </div>

                  </div>


                  <div className="claim-actions">

                    <button
                      className="approve-btn"
                      disabled={
                        actionLoading ===
                        `approve-claim-${claim.id}`
                      }
                      onClick={() =>
                        approveClaim(
                          claim.id
                        )
                      }
                    >

                      {actionLoading ===
                      `approve-claim-${claim.id}`
                        ? "Approving..."
                        : "✓ Approve"}

                    </button>


                    <button
                      className="reject-btn"
                      disabled={
                        actionLoading ===
                        `reject-claim-${claim.id}`
                      }
                      onClick={() =>
                        rejectClaim(
                          claim.id
                        )
                      }
                    >

                      {actionLoading ===
                      `reject-claim-${claim.id}`
                        ? "Rejecting..."
                        : "✕ Reject"}

                    </button>

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </section>

    </div>
  );
}

// ============================================================
// APP
// ============================================================

function App() {

  // ==========================================================
  // USER
  // ==========================================================

  const [user, setUser] =
    useState(null);


  // ==========================================================
  // DARK MODE
  // ==========================================================

  const [darkMode, setDarkMode] =
    useState(() => {

      return (
        localStorage.getItem(
          "refindx_theme"
        ) === "dark"
      );

    });


    useEffect(() => {

  console.log("DARK MODE:", darkMode);

  document.body.classList.toggle(
    "dark-mode",
    darkMode
  );

  localStorage.setItem(
    "refindx_theme",
    darkMode ? "dark" : "light"
  );

}, [darkMode]);



  // ==========================================================
  // LOAD SAVED USER
  // ==========================================================

  useEffect(() => {

    const savedUser =
      localStorage.getItem(
        "refindx_user"
      );


    if (savedUser) {

      try {

        setUser(
          JSON.parse(
            savedUser
          )
        );

      } catch {

        localStorage.removeItem(
          "refindx_user"
        );

      }

    }

  }, []);


  // ==========================================================
  // DARK MODE EFFECT
  // ==========================================================

  useEffect(() => {

    if (darkMode) {

      document.body.classList.add(
        "dark-mode"
      );

      localStorage.setItem(
        "refindx_theme",
        "dark"
      );

    } else {

      document.body.classList.remove(
        "dark-mode"
      );

      localStorage.setItem(
        "refindx_theme",
        "light"
      );

    }

  }, [darkMode]);


  return (

    <>

      <Navbar
        user={user}
        setUser={setUser}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />

      <AIChatbot />


      <main>

        <Routes>

          <Route
            path="/"
            element={
              <Home />
            }
          />


          <Route
            path="/items/:itemId"
            element={
              <ItemDetails
                user={user}
              />
            }
          />


          <Route
            path="/claims"
            element={
              <MyClaims
                user={user}
              />
            }
          />


          <Route
            path="/login"
            element={
              <Login
                setUser={setUser}
              />
            }
          />


          <Route
            path="/signup"
            element={
              <Signup
                setUser={setUser}
              />
            }
          />


          <Route
            path="/report"
            element={
              <ReportItem
                user={user}
              />
            }
          />


          <Route
            path="/notifications"
            element={
              <Notifications />
            }
          />


          <Route
            path="/admin"
            element={
              <AdminDashboard
                user={user}
              />
            }
          />

        </Routes>

      </main>


      <footer>

        <div className="footer-brand">
          ReFindX
        </div>


        <p>
          AI-powered community lost & found.
        </p>


        <span>
          © 2026 ReFindX
        </span>

      </footer>

    </>

  );
}
export default App;