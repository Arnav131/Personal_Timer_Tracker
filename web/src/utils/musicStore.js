const DB_NAME = 'productivity-enforcer-music';
const DB_VERSION = 1;
const STORE_NAME = 'tracks';

function openDatabase() {
  return new Promise((resolve, reject) => {
    if (!('indexedDB' in window)) {
      reject(new Error('This browser cannot save music between visits.'));
      return;
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error('Could not open music storage.'));
  });
}

function runTransaction(mode, operation) {
  return openDatabase().then(db => new Promise((resolve, reject) => {
    let transaction;
    let request;
    let result;

    try {
      transaction = db.transaction(STORE_NAME, mode);
      request = operation(transaction.objectStore(STORE_NAME));
    } catch (error) {
      db.close();
      reject(error);
      return;
    }

    request.onsuccess = () => { result = request.result; };
    request.onerror = () => reject(request.error || new Error('Music storage operation failed.'));
    transaction.oncomplete = () => {
      db.close();
      resolve(result);
    };
    transaction.onabort = transaction.onerror = () => {
      db.close();
      reject(transaction.error || new Error('Music storage transaction failed.'));
    };
  }));
}

export function getTracks() {
  return runTransaction('readonly', store => store.getAll());
}

export function saveTrack(track) {
  return runTransaction('readwrite', store => store.put(track));
}

export function deleteTrack(id) {
  return runTransaction('readwrite', store => store.delete(id));
}
