import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Drill Evaluation Dashboard",
  description: "Next.js dashboard for drill command evaluation and Python backend telemetry.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
