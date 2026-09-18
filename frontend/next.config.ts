import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
