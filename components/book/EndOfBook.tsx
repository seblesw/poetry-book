"use client";

import { book } from "@/content/book";
import { StoryImage } from "@/components/book/StoryImage";

export function EndOfBook() {
  const note = book.endNote;

  return (
    <div className="bk-book">
      <StoryImage src={book.endImage} alt={book.endAlt} priority />
      <div className="bk-spine" aria-hidden="true" />
      <section className="bk-page bk-end" aria-labelledby="end-heading">
        <div className="bk-page-head">
          <h2 id="end-heading" tabIndex={-1}>
            {note.heading}
          </h2>
          <hr className="bk-rule" />
        </div>
        <div className="bk-poem-scroll">
          {note.paragraphs.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
          <div className="bk-end-sign">
            {note.sign.map((line) => (
              <p key={line}>{line}</p>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
