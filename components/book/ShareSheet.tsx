"use client";

import { useEffect, useRef, useState } from "react";
import { IconClose } from "@/components/book/icons";

export function ShareSheet({
  title,
  url,
  onClose,
}: {
  title: string;
  url: string;
  onClose: () => void;
}) {
  const [note, setNote] = useState("");
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    closeRef.current?.focus();
  }, []);

  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
      setNote("አድራሻው ተቀድቷል።");
    } catch {
      setNote("መቅዳት አልተሳካም። አድራሻውን ይምረጡ።");
    }
  }

  return (
    <div className="bk-overlay is-share" onMouseDown={onClose}>
      <div
        className="bk-dialog is-share"
        role="dialog"
        aria-modal="true"
        aria-labelledby="share-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="bk-dialog-head">
          <h2 id="share-title">አጋራ</h2>
          <button ref={closeRef} className="bk-btn" type="button" onClick={onClose} aria-label="መጋሪያውን ዝጋ">
            <IconClose />
          </button>
        </div>
        <div className="bk-share">
          <p>{title}</p>
          <p>{url}</p>
          <button className="bk-btn" type="button" onClick={copy}>
            አድራሻውን ቅዳ
          </button>
          <p aria-live="polite">{note}</p>
        </div>
      </div>
    </div>
  );
}
