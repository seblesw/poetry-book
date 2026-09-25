import type { Poem } from "@/lib/poems";

export type PoemHit = {
  poem: Poem;
  preview: string;
};

export function searchPoems(poems: Poem[], query: string): PoemHit[] {
  const needle = query.trim().toLowerCase();
  if (!needle) return [];

  return poems.flatMap((poem) => {
    const title = poem.title.toLowerCase();
    const body = poem.text.toLowerCase();
    const titleHit = title.includes(needle);
    const at = body.indexOf(needle);
    if (!titleHit && at < 0) return [];

    let preview = "";
    if (at >= 0) {
      const start = Math.max(0, at - 20);
      const end = Math.min(poem.text.length, at + needle.length + 32);
      const slice = poem.text.slice(start, end).replace(/\s+/g, " ").trim();
      preview = `${start > 0 ? "…" : ""}${slice}${end < poem.text.length ? "…" : ""}`;
    }

    return [{ poem, preview }];
  });
}
