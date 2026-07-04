import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

export const metadata: Metadata = {
  title: "Turballoc — Turbulence-managed asset allocation",
  description:
    "A Mahalanobis turbulence index that scales portfolio risk in real time. Risk-parity base, volatility targeting, and a leak-safe turbulence overlay — validated by walk-forward backtests.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="min-h-screen bg-bg-deep font-sans text-text-primary antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[200] focus:rounded-md focus:bg-accent focus:px-4 focus:py-2 focus:font-medium focus:text-bg-deep"
        >
          Skip to content
        </a>
        {children}
      </body>
    </html>
  );
}
