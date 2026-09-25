"use client";

import Image from "next/image";
import { useState } from "react";

export function StoryImage({ src, alt, priority = false }: { src: string; alt: string; priority?: boolean }) {
  const [failed, setFailed] = useState(false);

  return (
    <div className="bk-story">
      {failed ? (
        <div className="bk-image-fallback" role="img" aria-label={alt}>
          <span aria-hidden="true">✶</span>
        </div>
      ) : (
        <Image
          src={src}
          alt={alt}
          fill
          priority={priority}
          sizes="(max-width: 959px) 100vw, 50vw"
          onError={() => setFailed(true)}
        />
      )}
    </div>
  );
}
