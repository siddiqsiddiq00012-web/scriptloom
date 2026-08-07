import React from "react";
import ReactDOM from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App";
import "./index.css";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

// Only wrap with GoogleOAuthProvider when a client ID is configured.
// An invalid/empty client ID would otherwise crash the entire app
// (breaking email/password login too). The Google button is further
// isolated by an error boundary in GoogleLoginButton.jsx.
const wrappedApp = googleClientId ? (
  <GoogleOAuthProvider clientId={googleClientId}>
    <App />
  </GoogleOAuthProvider>
) : (
  <App />
);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>{wrappedApp}</React.StrictMode>
);
