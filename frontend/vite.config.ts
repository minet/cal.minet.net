import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 5173,
    allowedHosts: [
      "localhost",
      "127.0.0.1",
      "cal-local.minet.net",
      "cal-dev.minet.net",
      "cal.minet.net",
    ],
    hmr: {
      clientPort: 443,
    },
  },
});
