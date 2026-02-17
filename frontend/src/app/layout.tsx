import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { LayoutContent } from "@/components/layout-content";
import { ProgressProvider } from "@/components/progress-provider";
import { Toaster } from "sonner"; // Import Toaster

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "KlandoDash",
  description: "Dashboard Klando",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <Providers>
          <ProgressProvider>
            <LayoutContent>{children}</LayoutContent>
          </ProgressProvider>
          <Toaster /> {/* Add Toaster component */}
        </Providers>
      </body>
    </html>
  );
}
