import "@fontsource-variable/archivo";
import "@fontsource-variable/source-serif-4";
import "./globals.css";

import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: {
    default: "ClickPe PIM",
    template: "%s | ClickPe PIM",
  },
  description: "Read-only public evidence from one finalized ClickPe Product Intelligence Monitor snapshot.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
