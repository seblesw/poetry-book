export const book = {
  title: "ማራኪ የፍቅር ግጥሞች",
  series: "የግጥም መድብል",
  issue: "፩",
  language: "am" as const,
  poet: "ኪዳነ ማርያም ዘውዱ",
  credit: "በኪዳነማርያም ዘውዱ የተዘጋጀ",
  date: "መስከረም 1 2019 ዓም",
  description: "ሃያ ስምንት ማራኪ የአማርኛ ግጥሞች። በኪዳነማርያም ዘውዱ የተዘጋጀ።",
  keywords: [
    "ማራኪ ፍቅር ግጥሞች",
    "የግጥም መድብል",
    "የአማርኛ ግጥም",
    "Amharic poetry",
    "digital poetry book",
  ],
  pdfFileName: "Achachir-Gitmoch-Digital-Poetry-Book.pdf",
  thumbnail: "/thumbnail.jpg",
  thumbnailAlt: "ማራኪ የፍቅር ግጥሞች። የግጥም መድብል። በኪዳነማርያም ዘውዱ የተዘጋጀ።",
  coverImage: "/plates/cover.jpg",
  coverAlt: "በቡናማ መስክ ላይ ነጭ ክፍት ቅርጽና የወርቅ ነጥብ ያለው የመጽሐፍ ምልክት።",
  endImage: "/plates/end.jpg",
  endAlt: "በቡናማ መስክ ላይ ነጭ ክብና የወርቅ መስመር ያለው ምልክት።",
  endNote: {
    heading: "ምስጋና",
    paragraphs: [
      "በቅድሚያ ለሁሉም ባለቤት ለልዑል እግዚአብሔር ክብር እና ምስጋና አምልኮት እና ውዳሴ ዛሬም ዘወትርም እስከ ዘለዓለም ድረስ ይሁን አሜን።",
  
      "በመጨረሻም የተለያዩ የግጥም ጽሁፎቼን በማንበብ ሀሳብ አስተያየት ለሰጣችሁኝ ሁሉ ከልብ አመሰግናለሁ።",
    ],
    sign: ["ኪዳነማርያም ዘውዱ|kidanyee@gmail.com", "መስከረም 1 2019 ዓ.ም", "አዲስ አበባ ኢትዮጵያ"],
  },
  /** Default reading music. The player can switch among the classical set. */
  ambient: "/audio/tizita.mp3",
};

export function siteUrl() {
  return process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
}
