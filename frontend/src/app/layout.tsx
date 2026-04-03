import type { Metadata } from "next";
import { Inter, Cairo } from "next/font/google";
import { cn } from "@/lib/utils";
import { Providers } from "./providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const cairo = Cairo({ subsets: ["arabic", "latin"], variable: "--font-arabic" });

export const metadata: Metadata = {
  title: "FiberHub Egypt — B2B Fiber Optic Network",
  description:
    "Egypt's trusted B2B platform for the fiber optic sector. Connect with suppliers, contractors, and buyers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans", inter.variable, cairo.variable)}>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
