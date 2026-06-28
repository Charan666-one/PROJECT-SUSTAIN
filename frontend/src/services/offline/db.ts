/**
 * IndexedDB wrapper for offline-first functionality
 * Caches: patient records, recent visits, downloaded knowledge snippets
 */
import { openDB } from "idb";

const DB_NAME = "homoeo-cdss-offline";
const DB_VERSION = 1;

export const getOfflineDB = () =>
  openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      db.createObjectStore("patients",      { keyPath: "id" });
      db.createObjectStore("visits",        { keyPath: "id" });
      db.createObjectStore("prescriptions", { keyPath: "id" });
      db.createObjectStore("pending_sync",  { keyPath: "id", autoIncrement: true });
    },
  });

export const cachePatient = async (patient: any) => {
  const db = await getOfflineDB();
  await db.put("patients", patient);
};

export const getCachedPatient = async (id: string) => {
  const db = await getOfflineDB();
  return db.get("patients", id);
};

export const queueForSync = async (action: any) => {
  const db = await getOfflineDB();
  await db.add("pending_sync", { ...action, queued_at: new Date().toISOString() });
};
