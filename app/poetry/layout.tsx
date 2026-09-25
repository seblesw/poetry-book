import { BookChrome } from "@/components/book/BookChrome";

export default function PoetryLayout({ children }: { children: React.ReactNode }) {
  return <BookChrome>{children}</BookChrome>;
}
