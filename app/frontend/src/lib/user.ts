import { v4 as uuidv4 } from "uuid";

export function newConversationId() {
  return `conv-${uuidv4()}`;
}

const USER_KEY = "cw_user_id";

export function getOrCreateUserId() {
  let id = localStorage.getItem(USER_KEY);
  if (!id) {
    id = uuidv4();
    localStorage.setItem(USER_KEY, id);
  }
  return id;
}
