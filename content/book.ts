export const book = {
  title: "አጫጭር ግጥሞች",
  series: "የግጥም መድብል",
  issue: "፩",
  language: "am" as const,
  description: "ሃያ ስምንት አጫጭር የአማርኛ ግጥሞች። የግጥም መድብል ዲጂታል መጽሐፍ።",
  keywords: [
    "አጫጭር ግጥሞች",
    "የግጥም መድብል",
    "የአማርኛ ግጥም",
    "Amharic poetry",
    "digital poetry book",
  ],
  pdfFileName: "Achachir-Gitmoch-Digital-Poetry-Book.pdf",
  coverImage: "/plates/cover.jpg",
  coverAlt: "የመጽሐፉ ሽፋን፤ ክፍት መጽሐፍ የሚመስል የቡና ቀለም ሥዕል።",
  endImage: "/plates/end.jpg",
  endAlt: "የመጽሐፉ መጨረሻ፤ በቡና ቀለም ውስጥ አንድ የወርቅ ነጥብ።",
  /** Optional ambient bed. Absent until a real audio file is added. */
  ambient: undefined as string | undefined,
};

export function siteUrl() {
  return process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
}
