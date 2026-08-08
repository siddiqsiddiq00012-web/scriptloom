import { Component } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { config } from "../../config";

/* Error boundary so a broken Google client ID never crashes the
   email/password login form. */
class GoogleLoginButton extends Component {
  constructor(props) {
    super(props);
    this.state = { failed: false };
  }

  static getDerivedStateFromError() {
    return { failed: true };
  }

  render() {
    if (this.state.failed) return null;
    if (!config.googleClientId) return null;
    return <GoogleLoginInner {...this.props} />;
  }
}

function GoogleLoginInner({ onError, onSuccess, loading }) {
  return (
    <div className="authCard__googleBtnWrapper">
      <GoogleLogin
        onSuccess={(credentialResponse) => {
          if (credentialResponse?.credential) {
            onSuccess(credentialResponse.credential);
          } else {
            onError("Google authentication failed.");
          }
        }}
        onError={() => onError("Google authentication failed.")}
        useOneTap={false}
        theme="outline"
        shape="pill"
        size="large"
        text="continue_with"
        width="100%"
        disabled={loading}
      />
    </div>
  );
}

export default GoogleLoginButton;
