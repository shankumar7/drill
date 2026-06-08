import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { EvaluationProvider } from "@/context/EvaluationContext";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Military Drill Analysis System",
  description: "Advanced biomechanical tracking and posture evaluation for military drills.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${outfit.variable} font-sans antialiased`}
      >
        <EvaluationProvider>
          {children}
        </EvaluationProvider>
      </body>
    </html>
  );
}
