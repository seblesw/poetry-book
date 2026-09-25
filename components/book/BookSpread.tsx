import type { Poem } from "@/lib/poems";
import { PoemPage } from "@/components/book/PoemPage";
import { StoryImage } from "@/components/book/StoryImage";

export function BookSpread({ poem, priority = false }: { poem: Poem; priority?: boolean }) {
  return (
    <div className="bk-book">
      <StoryImage src={poem.image} alt={poem.alt} priority={priority} />
      <div className="bk-spine" aria-hidden="true" />
      <PoemPage poem={poem} />
    </div>
  );
}
