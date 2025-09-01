import { useState } from "react";

export default function Composer({
  onSend,
  disabled,
}: {
  onSend: (text: string) => Promise<void> | void;
  disabled?: boolean;
}) {
  const [text, setText] = useState("");
  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const t = text.trim();
    if (!t || disabled) return;
    setText("");
    await onSend(t);
  };
  return (
    <form
      onSubmit={submit}
      className="flex items-center gap-3 p-3 bg-card rounded-xl2 border border-[#1f2937]"
    >
      <input
        className="flex-1 rounded-lg bg-[#0f172a] border border-[#1f2937] px-4 py-3 outline-none focus:border-accent"
        placeholder="Type your message…"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        type="submit"
        disabled={disabled}
        className="px-5 py-3 rounded-lg bg-accent text-black font-medium disabled:opacity-50"
      >
        Send
      </button>
    </form>
  );
}
