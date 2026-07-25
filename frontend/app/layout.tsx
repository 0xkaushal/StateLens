import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StateLens — Chrome DevTools for AI Agents",
  description: "Inspect, understand, and debug LangGraph execution",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-neutral-950 text-neutral-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
