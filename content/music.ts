export type Track = {
  id: string;
  title: string;
  composer: string;
  src: string;
};

/** Original pieces in Ethiopian qenet, made for reading. */
export const tracks: Track[] = [
  {
    id: "tizita",
    title: "ትዝታ",
    composer: "ክላሲካል",
    src: "/audio/tizita.mp3?v=3",
  },
  {
    id: "bati",
    title: "ባቲ",
    composer: "ክላሲካል",
    src: "/audio/bati.mp3?v=3",
  },
  {
    id: "ambassel",
    title: "አምባሰል",
    composer: "ክላሲካል",
    src: "/audio/ambassel.mp3?v=3",
  },
];

export const defaultTrackId = tracks[0].id;
