import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: "https://harshitantil.xyz",
      priority: 1,
      changeFrequency: "weekly",
    },
  ];
}
