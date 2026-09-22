import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname),
  },
  async rewrites() {
    const backendApi = process.env.NEXT_PUBLIC_API_URL || "https://yatri-setu.onrender.com/api";
    const cleanBackend = backendApi.replace(/\/+$/, "");
    return [
      {
        source: "/api/:path*",
        destination: `${cleanBackend}/:path*`,
      },
    ];
  },
};

export default nextConfig;
