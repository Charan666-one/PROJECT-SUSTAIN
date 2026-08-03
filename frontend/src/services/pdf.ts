/**
 * Open a PDF that requires an Authorization header.
 * A plain <a href> can't carry the JWT, so fetch the bytes then open a blob URL.
 */
export async function openPdf(url: string, token: string | null): Promise<void> {
  const res = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  if (!res.ok) throw new Error("Could not load the PDF.");
  const blobUrl = URL.createObjectURL(await res.blob());
  window.open(blobUrl, "_blank");
  setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
}
