import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config) => {
    // resolve fs for one of the dependencies
    config.resolve.fallback = {
      fs: false
    };

    // loading our wasm files as assets
    config.module.rules.push({
      test: /\.wasm/,
      type: "asset/resource"
    });

    return config;
  }
};

export default nextConfig;
