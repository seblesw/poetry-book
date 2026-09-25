import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  images: {
    formats: ["image/avif", "image/webp"],
  },
  outputFileTracingIncludes: {
    "/api/poetry/pdf": ["./assets/fonts/**/*", "./public/plates/**/*"],
  },
  async headers() {
    return [
      {
        source: "/pdf/:file*",
        headers: [
          { key: "Content-Type", value: "application/pdf" },
          { key: "Cache-Control", value: "public, max-age=0, must-revalidate" },
        ],
      },
    ];
  },
};

export default nextConfig;
