import React from "react";

/** Catches render errors so a bug never leaves the user staring at a blank screen. */
export default class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.error("Render error caught by ErrorBoundary:", error);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="center-screen">
        <div className="card" style={{ maxWidth: 420, textAlign: "center" }}>
          <h2>Something went wrong</h2>
          <p className="muted">An unexpected error occurred. Reloading usually fixes it.</p>
          <button className="btn" style={{ marginTop: ".5rem" }} onClick={() => { location.href = "/"; }}>
            Reload app
          </button>
        </div>
      </div>
    );
  }
}
