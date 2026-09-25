import type { MetadataRoute } from "next";
import { siteUrl } from "@/content/book";
import { END_SLUG, poems } from "@/lib/poems";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteUrl();
  return [
    { url: base, changeFrequency: "monthly", priority: 1 },
    ...poems.map((poem) => ({
      url: `${base}/poetry/${poem.slug}`,
      changeFrequency: "yearly" as const,
      priority: 0.8,
    })),
    { url: `${base}/poetry/${END_SLUG}`, changeFrequency: "yearly", priority: 0.3 },
  ];
}
