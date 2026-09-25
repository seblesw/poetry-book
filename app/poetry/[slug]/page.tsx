import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { book } from "@/content/book";
import { END_SLUG, getPoem, poemCount, poems } from "@/lib/poems";
import { PoetryBook } from "@/components/book/PoetryBook";

type Params = { slug: string };

export function generateStaticParams() {
  return [...poems.map((poem) => ({ slug: poem.slug })), { slug: END_SLUG }];
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { slug } = await params;
  if (slug === END_SLUG) {
    return {
      title: "መጨረሻ",
      description: `${book.endNote.subtitle} — ${book.endNote.heading}`,
      alternates: { canonical: "/poetry/end" },
    };
  }
  const poem = getPoem(slug);
  if (!poem) return {};
  const description = poem.description ?? poem.title;
  return {
    title: poem.title,
    description,
    alternates: { canonical: `/poetry/${poem.slug}` },
    openGraph: {
      title: `${poem.title} · ${book.title}`,
      description,
      locale: "am_ET",
      type: "article",
      images: [{ url: poem.image, alt: poem.alt }],
    },
    twitter: {
      card: "summary_large_image",
      title: `${poem.title} · ${book.title}`,
      description,
      images: [poem.image],
    },
  };
}

export default async function PoemRoute({ params }: { params: Promise<Params> }) {
  const { slug } = await params;
  const poem = slug === END_SLUG ? null : getPoem(slug);
  if (!poem && slug !== END_SLUG) notFound();

  const jsonLd = poem
    ? {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        name: poem.title,
        text: poem.text,
        inLanguage: "am",
        position: poem.number,
        image: poem.image,
        isPartOf: {
          "@type": "Book",
          name: book.title,
          numberOfPages: poemCount,
        },
      }
    : {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        name: `${book.title} — መጨረሻ`,
        inLanguage: "am",
        isPartOf: { "@type": "Book", name: book.title },
      };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <PoetryBook slug={slug} />
    </>
  );
}
