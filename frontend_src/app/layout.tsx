import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./main.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "IQLAWD LAB - Trust Intelligence",
    description: "Agent Trust Intelligence Dashboard",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <script
                    dangerouslySetInnerHTML={{
                        __html: `
              if (typeof window !== 'undefined') {
                if (!window.crypto) window.crypto = {};
                if (!window.crypto.randomUUID) {
                  window.crypto.randomUUID = function() {
                    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                      return v.toString(16);
                    });
                  };
                }
              }
            `,
                    }}
                />
                {children}
            </body>
        </html>
    );
}
