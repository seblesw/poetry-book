"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { book } from "@/content/book";

export function BookCover() {
  const router = useRouter();

  function openBook() {
    window.sessionStorage.setItem("poetry-open", "1");
    window.sessionStorage.setItem("poetry-dir", "next");
    router.push("/poetry/1");
  }

  return (
    <main className="cv">
      <article className="cv-jacket">
        <div className="cv-art">
          <Image src={book.coverImage} alt={book.coverAlt} fill priority sizes="(max-width: 959px) 100vw, 50vw" />
        </div>
        <div className="cv-copy">
          <p className="cv-series">
            {book.series} · {book.issue}
          </p>
          <h1>{book.title}</h1>
          <hr className="cv-rule" />
          <p className="cv-sub">ሃያ ስምንት አጫጭር ግጥሞች</p>
          <button className="cv-open" type="button" onClick={openBook}>
            መጽሐፉን ክፈት
          </button>
        </div>
      </article>
    </main>
  );
}
