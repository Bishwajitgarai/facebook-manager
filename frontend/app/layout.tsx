import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OmniReels Studio - AI Video Generator & Social Sync",
  description: "Autonomous Gemini Video Creation, Neural Voiceover & Social Publishing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-950 text-slate-100 font-sans">
        {children}
      </body>
    </html>
  );
}
