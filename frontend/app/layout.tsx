import type { Metadata } from "next";
import "./globals.css";
import Navbar from "../components/Navbar";

export const metadata: Metadata = {
  title: "AeroGuard — AI + IoT Hyperlocal Environmental Intelligence",
  description: "AIoT platform for Predicting and Preventing Air Pollution Risks in Delhi NCR using CPCB Standards, Machine Learning, and Hyperlocal IoT Telemetry.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>AeroGuard — Team Victory Vanguard (Shanmukha Reddy)</span>
            <span>Complementary AIoT Intelligence Layer for CPCB Infrastructure</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
