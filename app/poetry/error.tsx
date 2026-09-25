"use client";

export default function PoetryError({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="bk-fallback">
      <div>
        <h1>ንባቡ አልተከፈተም</h1>
        <button type="button" onClick={reset}>
          እንደገና ሞክር
        </button>
      </div>
    </main>
  );
}
