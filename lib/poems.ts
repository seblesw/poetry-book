import raw from "@/content/poems.json";
import { book } from "@/content/book";

export type Poem = {
  id: string;
  number: number;
  slug: string;
  title: string;
  text: string;
  image: string;
  alt: string;
  description?: string;
  audio?: string;
};

type PoemFile = {
  source: string;
  title: string;
  series: string;
  poems: Poem[];
};

const data = raw as PoemFile;

export const poems: Poem[] = data.poems;
export const poemSource = data.source;
export const poemCount = poems.length;
export const END_SLUG = "end";
export const COVER_SLUG = "cover";

if (poemCount !== 28) {
  throw new Error(`Expected 28 poems, found ${poemCount}.`);
}

export function getPoem(slug: string): Poem | undefined {
  return poems.find((poem) => poem.slug === slug);
}

export function neighbors(slug: string): { prev: string | null; next: string | null } {
  if (slug === END_SLUG) {
    return { prev: String(poemCount), next: null };
  }
  const poem = getPoem(slug);
  if (!poem) return { prev: null, next: null };
  return {
    prev: poem.number > 1 ? String(poem.number - 1) : COVER_SLUG,
    next: poem.number < poemCount ? String(poem.number + 1) : END_SLUG,
  };
}

export function audioFor(poem?: Poem | null): string | null {
  return poem?.audio || book.ambient || null;
}

export { book };
