import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Econe Papers - 经济学论文精选",
  description: "每日自动抓取 arXiv 经济学论文，AI 筛选分类，展示精选论文",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-gray-50">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
