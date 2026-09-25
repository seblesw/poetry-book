import { poemCount } from "@/lib/poems";

export function ProgressIndicator({ number, ended = false }: { number?: number; ended?: boolean }) {
  if (ended) {
    return (
      <p className="bk-progress" aria-label="መጨረሻ">
        <span>መጨረሻ</span>
      </p>
    );
  }
  const label = `${String(number).padStart(2, "0")} ከ ${String(poemCount).padStart(2, "0")}`;
  return (
    <p className="bk-progress" aria-label={label}>
      <span>{String(number).padStart(2, "0")}</span>
      <span className="bk-progress-rule" aria-hidden="true" />
      <span>{String(poemCount).padStart(2, "0")}</span>
    </p>
  );
}
