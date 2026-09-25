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
    composer: "ክራር",
    src: "/audio/tizita.mp3",
  },
  {
    id: "bati",
    title: "ባቲ",
    composer: "መሰንቆ",
    src: "/audio/bati.mp3",
  },
  {
    id: "ambassel",
    title: "አምባሰል",
    composer: "ዋሽንት",
    src: "/audio/ambassel.mp3",
  },
];

export const defaultTrackId = tracks[0].id;
