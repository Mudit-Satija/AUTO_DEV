import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AUTO.DEV - AI Orchestration",
  description: "AI-powered backend architecture planning",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90' fill='%233b82f6'>⚙</text></svg>" />
      </head>
      <body className="bg-gradient-to-br from-slate-950 via-slate-900 to-black text-slate-50">
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/10 via-transparent to-purple-900/10" />
          <div className="absolute top-1/4 -left-32 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] animate-glow-pulse" />
          <div className="absolute bottom-1/4 -right-32 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px] animate-glow-pulse" style={{ animationDelay: '2s' }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-400/5 rounded-full blur-[150px]" />
        </div>
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  );
}
