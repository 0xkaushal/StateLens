import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", // Static HTML export — no Node.js server needed
  distDir: "out",   // Output to frontend/out/
};

export default nextConfig;
