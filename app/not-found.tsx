import Link from "next/link";

export default function NotFound() {
  return (
    <main className="bk-fallback">
      <div>
        <h1>ይህ ገጽ አልተገኘም</h1>
        <p>
          <Link href="/">ወደ መጽሐፉ ተመለስ</Link>
        </p>
      </div>
    </main>
  );
}
