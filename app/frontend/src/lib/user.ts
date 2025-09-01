export function getOrCreateUserId(): string {
  const KEY = "chat-user-id";
  let uid = localStorage.getItem(KEY);
  if (!uid) {
    uid = `u-${crypto.randomUUID()}`;
    localStorage.setItem(KEY, uid);
  }
  return uid;
}
