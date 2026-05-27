// React hook used for storing and updating UI state
//
// useState allows the frontend to reactively update the page
// whenever values change
//
// examples:
// - user typing query
// - loading spinner
// - backend JSON response
import { useEffect, useState } from "react";

// import CSS styling file for component styles/layout
import "./App.css";


// default example query shown when UI first loads
//
// helps demonstrate supported natural language requests
const DEFAULT_QUERY =
  "Show me all orders where the buyer was located in Ohio and total value was over 500.";


const TYPEWRITER_TEXT =
  "Show me all orders where the buyer was located in Ohio and total value was over 500.";

const TYPING_SPEED = 45;
const DELETING_SPEED = 25;
const PAUSE_AFTER_TYPING = 1200;
const PAUSE_AFTER_DELETING = 500;
const MIN_DELETE_LENGTH = 20;


// main React component
//
// responsible for:
// - rendering UI
// - handling user input
// - calling backend Flask API
// - displaying structured JSON results
function App() {

  const [animatedPlaceholder, setAnimatedPlaceholder] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [isInputFocused, setIsInputFocused] = useState(false);
  // stores current user query typed into textarea
  //
  // example:
  // "orders in ohio over 500"
  const [query, setQuery] = useState("");

  // stores final backend JSON response
  //
  // example:
  // {
  //   orders: [...]
  // }
  const [result, setResult] = useState(null);

  // loading state used to disable button and show spinner text
  //
  // prevents duplicate submissions while backend is processing
  const [loading, setLoading] = useState(false);

  // stores frontend error messages
  //
  // examples:
  // - backend unavailable
  // - invalid request
  // - network failure
  const [error, setError] = useState("");

  useEffect(() => {
    if (isInputFocused || query.length > 0) {
      return;
    }
  
    const currentLength = animatedPlaceholder.length;
  
    let timeoutDelay = isDeleting ? DELETING_SPEED : TYPING_SPEED;
  
    if (!isDeleting && currentLength === TYPEWRITER_TEXT.length) {
      timeoutDelay = PAUSE_AFTER_TYPING;
    }
  
    if (isDeleting && currentLength === 0) {
      timeoutDelay = PAUSE_AFTER_DELETING;
    }
  
    const timer = setTimeout(() => {
      if (!isDeleting) {
        if (currentLength < TYPEWRITER_TEXT.length) {
          setAnimatedPlaceholder(TYPEWRITER_TEXT.slice(0, currentLength + 1));
        } else {
          setIsDeleting(true);
        }
      } else {
        if (currentLength > 0) {

          // randomly decide how much text to keep
          const randomStopPoint =
            Math.floor(
              Math.random() *
              (TYPEWRITER_TEXT.length - MIN_DELETE_LENGTH)
            ) + MIN_DELETE_LENGTH;
        
          // continue deleting until random stop point reached
          if (currentLength > randomStopPoint) {
        
            setAnimatedPlaceholder(
              TYPEWRITER_TEXT.slice(0, currentLength - 1)
            );
        
          } else {
        
            // begin typing again from partial sentence
            setIsDeleting(false);
          }
        
        } else {
        
          setIsDeleting(false);
        }
      }
    }, timeoutDelay);
  
    return () => clearTimeout(timer);
  }, [animatedPlaceholder, isDeleting, isInputFocused, query]);

  // async function responsible for executing the customer order agent
  //
  // frontend -> Flask backend -> LangGraph workflow
  async function runAgent() {

    // enable loading state while backend request runs
    setLoading(true);

    // clear previous error messages
    setError("");

    // clear previous results before new request
    setResult(null);

    try {

      // send POST request to Flask backend API
      //
      // backend endpoint:
      // http://localhost:8000/agent
      //
      // request body:
      // {
      //   "query": "orders in ohio over 500"
      // }
      const response = await fetch("http://localhost:8000/agent", {

        // HTTP method used for sending data to backend
        method: "POST",

        // tells backend request body contains JSON
        headers: {
          "Content-Type": "application/json",
        },

        // convert JavaScript object into JSON string
        body: JSON.stringify({
          query: query,
        }),
      });

      // convert backend JSON response into JavaScript object
      const data = await response.json();

      // defensive frontend validation
      //
      // if backend returned HTTP error:
      // - 400
      // - 500
      // etc.
      //
      // throw frontend error
      if (!response.ok) {

        throw new Error(
          data.error || "Failed to run agent"
        );
      }

      // store successful backend response in React state
      //
      // this automatically re-renders UI with results
      setResult(data);

    } catch (err) {

      // capture network/backend/frontend failures
      //
      // examples:
      // - backend offline
      // - Flask crash
      // - invalid response
      // - CORS issue
      setError(err.message);

    } finally {

      // disable loading state once request finishes
      //
      // finally ALWAYS runs:
      // success or failure
      setLoading(false);
    }
  }


  return (
    <main className="app-container">
      <div className="top-banner">Customer Order AI Agent</div>
  
      <section className="hero">
        <p className="eyebrow">Structured order intelligence</p>
        <h1>Search Customer Orders</h1>
        <p className="description">
          Enter a natural language request and run a structured agent workflow
          that retrieves messy order records, validates the output, and returns
          clean JSON results.
        </p>
      </section>
  
      <section className="card">
        <label htmlFor="query">
  Order query
</label>

<div className="textarea-wrapper">

  {/* animated fake placeholder */}
  {!query && !isInputFocused && (

    <div className="animated-placeholder">

      {animatedPlaceholder}

      <span className="cursor">
        |
      </span>

    </div>
  )}

  <textarea
    id="query"

    value={query}

    onChange={(event) =>
      setQuery(event.target.value)
    }

    // hide animation while user focused textarea
    onFocus={() =>
      setIsInputFocused(true)
    }

    // allow animation again if textarea empty
    onBlur={() =>
      setIsInputFocused(false)
    }

    rows={5}
  />

</div>
  
        <button onClick={runAgent} disabled={loading}>
          {loading ? "Running agent..." : "Run Agent"}
        </button>
  
        {error && <p className="error">{error}</p>}
  
        {result && (
          <section className="results">
            <h2>Final JSON Response</h2>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </section>
        )}
      </section>
    </main>
  );
}

// export component so Vite/React can render it
export default App;