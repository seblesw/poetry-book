"use client";

import Image from "next/image";
import Link from "next/link";
import { book } from "@/content/book";

export function BookCover() {
  function rememberOpen() {
    window.sessionStorage.setItem("poetry-open", "1");
    window.sessionStorage.setItem("poetry-dir", "next");
  }

  return (
    <main className="cv">
      <article className="cv-jacket">
        <div className="cv-art">
          <Image src={book.coverImage} alt={book.coverAlt} fill priority sizes="(max-width: 959px) 100vw, 50vw" style={{ objectFit: "contain", objectPosition: "center" }} />
        </div>
        <div className="cv-copy">
          <p className="cv-series">
            {book.series} · {book.issue}
          </p>
          <h1>{book.title}</h1>
          <hr className="cv-rule" />
          <p className="cv-sub">ሃያ ስምንት አጫጭር ግጥሞች</p>
          <p className="cv-credit">{book.credit}</p>
          <Link className="cv-open" href="/poetry/1" onClick={rememberOpen}>
            መጽሐፉን ክፈት
          </Link>
        </div>
      </article>
    </main>
  );
}
