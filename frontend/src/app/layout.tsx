import type { Metadata } from "next";
import Providers from "@/components/Providers";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://harshitantil.xyz"),

  title: {
    default: "TraceOS | Personal & Company Operating System",
    template: "%s | TraceOS",
  },

  description:
    "TraceOS is an AI-powered personal and company operating system built by Harshit Antil. Organize projects, meetings, finance, decisions, knowledge, entities, and workflows in one intelligent workspace.",

  keywords: [
    "TraceOS",
    "Harshit Antil",
    "AI",
    "Knowledge Management",
    "Personal OS",
    "Company OS",
    "Productivity",
    "Second Brain",
    "Graph",
    "Decision Making",
    "Projects",
    "Workspace",
  ],

  authors: [
    {
      name: "Harshit Antil",
      url: "https://harshitantil.xyz",
    },
  ],

  creator: "Harshit Antil",

  publisher: "Harshit Antil",

  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },

  openGraph: {
    title: "TraceOS",
    description:
      "An AI-powered operating system for your life and company.",
    url: "https://harshitantil.xyz",
    siteName: "TraceOS",
    locale: "en_US",
    type: "website",
  },

  twitter: {
    card: "summary_large_image",
    title: "TraceOS",
    description:
      "AI-powered personal and company operating system.",
  },

  alternates: {
    canonical: "https://harshitantil.xyz",
  },

  category: "technology",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
