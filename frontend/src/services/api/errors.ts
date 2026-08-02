/**
 * Turn any API error into a readable string.
 * FastAPI validation errors (422) return `detail` as an ARRAY of objects — passing
 * that straight to React as a child crashes the tree, so always normalise here.
 */
export function getErrorMessage(err: any, fallback = "Something went wrong. Please try again."): string {
  const d = err?.response?.data?.detail;
  if (typeof d === "string" && d) return d;
  if (Array.isArray(d)) {
    const msgs = d.map((e) => (typeof e === "string" ? e : e?.msg || e?.message)).filter(Boolean);
    if (msgs.length) return msgs.join(" · ");
  }
  if (d && typeof d === "object" && (d.msg || d.message)) return d.msg || d.message;
  if (typeof err?.message === "string" && err.message && err.message !== "Network Error") return err.message;
  if (err?.message === "Network Error") return "Can't reach the server. Is the backend running?";
  return fallback;
}
