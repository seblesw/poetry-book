export function PoemText({ text }: { text: string }) {
  const stanzas: string[][] = [];
  let current: string[] = [];
  for (const line of text.split("\n")) {
    if (!line.trim()) {
      if (current.length) stanzas.push(current);
      current = [];
    } else {
      current.push(line);
    }
  }
  if (current.length) stanzas.push(current);

  return (
    <div className="bk-poem-text">
      {stanzas.map((stanza, index) => (
        <p key={index}>
          {stanza.map((line, lineIndex) => (
            <span className="bk-line" key={lineIndex}>
              {line}
            </span>
          ))}
        </p>
      ))}
    </div>
  );
}
