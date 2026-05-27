// React hook used for storing and updating UI state
//
// useState allows the frontend to reactively update the page
// whenever values change
//
// examples:
// - user typing query
// - loading spinner
// - backend JSON response
import { useState } from "react";

// import CSS styling file for component styles/layout
import "./App.css";


// default example query shown when UI first loads
//
// helps demonstrate supported natural language requests
const DEFAULT_QUERY =
  "Show me all orders where the buyer was located in Ohio and total value was over 500.";


// main React component
//
// responsible for:
// - rendering UI
// - handling user input
// - calling backend Flask API
// - displaying structured JSON results
function App() {

  // stores current user query typed into textarea
  //
  // example:
  // "orders in ohio over 500"
  const [query, setQuery] = useState(DEFAULT_QUERY);

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

    // main page container
    <main className="app-container">

      {/* centered UI card */}
      <section className="card">

        {/* small top label */}
        <p className="eyebrow">
          Customer Order Agent
        </p>

        {/* main title */}
        <h1>
          Search messy customer orders with a structured agent workflow
        </h1>

        {/* project description */}
        <p className="description">

          This interface sends a natural language request to a Flask backend,
          runs the LangGraph workflow, parses unstructured order text, validates
          the output, and returns filtered JSON results.

        </p>

        {/* textarea label */}
        <label htmlFor="query">
          Order query
        </label>

        {/* multi-line text input */}
        <textarea
          id="query"

          // current textarea value
          value={query}

          // update query state when user types
          onChange={(event) =>
            setQuery(event.target.value)
          }

          // textarea size
          rows={5}
        />

        {/* execute workflow button */}
        <button

          // run backend workflow when clicked
          onClick={runAgent}

          // disable button while backend request running
          disabled={loading}
        >

          {/* conditional rendering */}
          {loading
            ? "Running agent..."
            : "Run Agent"}

        </button>

        {/* display frontend/backend error message */}
        {error && (
          <p className="error">
            {error}
          </p>
        )}

        {/* display backend JSON results if available */}
        {result && (

          <section className="results">

            <h2>
              Final JSON Response
            </h2>

            {/* pretty-print JSON results */}
            <pre>
              {JSON.stringify(result, null, 2)}
            </pre>

          </section>
        )}
      </section>
    </main>
  );
}

// export component so Vite/React can render it
export default App;