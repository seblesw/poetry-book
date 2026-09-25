export const book = {
  title: "አጫጭር ግጥሞች",
  series: "የግጥም መድብል",
  issue: "፩",
  language: "am" as const,
  poet: "ኪዳነ ማርያም ዘውዱ",
  credit: "በ ገጣሚ ኪዳነ ማርያም ዘውዱ የተዘጋጀ",
  description: "ሃያ ስምንት አጫጭር የአማርኛ ግጥሞች። በ ገጣሚ ኪዳነ ማርያም ዘውዱ የተዘጋጀ።",
  keywords: [
    "አጫጭር ግጥሞች",
    "የግጥም መድብል",
    "የአማርኛ ግጥም",
    "Amharic poetry",
    "digital poetry book",
  ],
  pdfFileName: "Achachir-Gitmoch-Digital-Poetry-Book.pdf",
  coverImage: "/plates/cover.jpg",
  coverAlt: "በቡናማ መስክ ላይ ነጭ ክፍት ቅርጽና የወርቅ ነጥብ ያለው የመጽሐፍ ምልክት።",
  endImage: "/plates/end.jpg",
  endAlt: "መጽሐፉን ይዞ በጸጥታ የቆመ ሰው።",
  /** Default reading music. The player can switch among the classical set. */
  ambient: "/audio/tizita.mp3",
};

export function siteUrl() {
  return process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
}
