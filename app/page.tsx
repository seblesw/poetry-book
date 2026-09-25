import type { Metadata } from "next";
import { book, siteUrl } from "@/content/book";
import { poemCount } from "@/lib/poems";
import { BookCover } from "@/components/book/BookCover";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

export default function HomePage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Book",
    name: book.title,
    inLanguage: "am",
    bookFormat: "https://schema.org/EBook",
    genre: "Poetry",
    numberOfPages: poemCount,
    description: book.description,
    url: siteUrl(),
    isPartOf: {
      "@type": "CreativeWorkSeries",
      name: book.series,
    },
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <BookCover />
    </>
  );
}
