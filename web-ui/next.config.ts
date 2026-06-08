import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ['@tensorflow-models/pose-detection', '@mediapipe/pose'],
};

export default nextConfig;
