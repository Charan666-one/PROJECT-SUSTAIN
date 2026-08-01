/** Small reusable state components: loading, error, empty. */
export function Loading({ label = "Loading…" }: { label?: string }) {
  return <div className="card muted" role="status" aria-live="polite">{label}</div>;
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
