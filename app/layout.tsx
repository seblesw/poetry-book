import type { Metadata } from "next";
import localFont from "next/font/local";
import { book, siteUrl } from "@/content/book";
import "./globals.css";

const abyssinica = localFont({
  src: "../assets/fonts/AbyssinicaSIL-R.ttf",
  variable: "--font-abyssinica",
  display: "swap",
  adjustFontFallback: false,
});

const emoji = localFont({
  src: "../assets/fonts/NotoEmoji-Regular.ttf",
  variable: "--font-emoji",
  display: "swap",
  adjustFontFallback: false,
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title: {
    default: book.title,
    template: `%s · ${book.title}`,
  },
  description: book.description,
  authors: [{ name: book.poet }],
  keywords: [...book.keywords],
  openGraph: {
    title: book.title,
    description: book.description,
    locale: "am_ET",
    type: "website",
    images: [{ url: book.coverImage, alt: book.coverAlt }],
  },
  twitter: {
    card: "summary_large_image",
    title: book.title,
    description: book.description,
    images: [book.coverImage],
  },
};

const themeScript = `try{var t=localStorage.getItem("poetry-theme");if(t!=="dark"&&t!=="light"){t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}document.documentElement.dataset.theme=t;}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="am" className={`${abyssinica.variable} ${emoji.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
