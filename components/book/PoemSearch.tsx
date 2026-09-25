"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { poems } from "@/lib/poems";
import { searchPoems } from "@/lib/search";
import { IconClose } from "@/components/book/icons";

export function PoemSearch({
  onClose,
  onSelect,
}: {
  onClose: () => void;
  onSelect: (slug: string) => void;
}) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const hits = useMemo(() => searchPoems(poems, query), [query]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="bk-overlay is-search" onMouseDown={onClose}>
      <div
        className="bk-dialog is-search"
        role="dialog"
        aria-modal="true"
        aria-labelledby="search-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="bk-dialog-head">
          <h2 id="search-title">ፈልግ</h2>
          <button className="bk-btn" type="button" onClick={onClose} aria-label="ፍለጋውን ዝጋ">
            <IconClose />
          </button>
        </div>
        <input
          ref={inputRef}
          className="bk-search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="ርዕስ ወይም የግጥም ቃል"
          aria-label="ግጥም ፈልግ"
          type="search"
        />
        {query.trim() ? (
          hits.length ? (
            <ul className="bk-results">
              {hits.map((hit) => (
                <li key={hit.poem.id}>
                  <button type="button" onClick={() => onSelect(hit.poem.slug)}>
                    <span className="bk-num">{String(hit.poem.number).padStart(2, "0")}</span>
                    <span>{hit.poem.title}</span>
                    {hit.preview ? <small>{hit.preview}</small> : null}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="bk-empty">ምንም አልተገኘም።</p>
          )
        ) : (
          <p className="bk-empty">የግጥም ርዕስ ወይም ቃል ይጻፉ።</p>
        )}
      </div>
    </div>
  );
}
