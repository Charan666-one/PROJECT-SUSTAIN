/** Small reusable state components: loading, error, empty. */
export function Loading() {
  return (
    <div className="card" role="status" aria-live="polite" aria-busy="true">
      <span className="sr-only">Loading…</span>
      <div className="skeleton" style={{ width: "40%", height: 18, marginBottom: 14 }} />
      <div className="skeleton" style={{ width: "100%", height: 12, marginBottom: 8 }} />
      <div className="skeleton" style={{ width: "85%", height: 12, marginBottom: 8 }} />
      <div className="skeleton" style={{ width: "60%", height: 12 }} />
    </div>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return <div className="error" role="alert">{message}</div>;
}

export function Empty({ children }: { children: React.ReactNode }) {
  return <div className="card muted">{children}</div>;
}

/** Wraps an async area: shows loading / error / content. */
export function Async<T>({ loading, error, data, children, empty }: {
  loading: boolean; error?: string; data: T | null;
  children: (d: T) => React.ReactNode; empty?: React.ReactNode;
}) {
  if (loading) return <Loading />;
  if (error) return <ErrorNote message={error} />;
  if (!data) return <>{empty ?? <Empty>Nothing to show.</Empty>}</>;
  return <>{children(data)}</>;
}
