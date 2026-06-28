import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
        runtimeCaching: [
          {
            urlPattern: /\/api\/v1\/patients/,
            handler: "StaleWhileRevalidate",
            options: { cacheName: "patient-cache" },
          },
        ],
      },
      manifest: {
        name: "Homoeo CDSS",
        short_name: "HoMoeo",
        theme_color: "#1a5276",
        icons: [{ src: "/icon-192.png", sizes: "192x192", type: "image/png" }],
      },
    }),
  ],
  server: { proxy: { "/api": "http://localhost:8000" } },
});
