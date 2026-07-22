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
  title: "SDD-MDAS",
  description: "Simulation Development Division - Military Drill Analysis System",
  icons: {
    icon: "/top_right_logo.png",
    shortcut: "/top_right_logo.png",
    apple: "/top_right_logo.png",
  },
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
