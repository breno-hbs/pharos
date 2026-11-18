import type { Metadata } from "next";
import "@fontsource-variable/inter";
import "./globals.css";

export const metadata: Metadata = {
  title: "PHAROS | Mobilidade no Capão Redondo",
  icons: { icon: "/logo.png" },
  description: "Planeje e compare trajetos no território piloto do Capão Redondo.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
