import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    modules: {
      localsConvention: 'dashes',
    }
  }
  ,
  server: {
    // allow binding to network interfaces (useful in Docker / remote dev)
    host: true,
    // allow specific hostnames (add internationalized domain name provided)
    allowedHosts: ["test.xn--80aaaaga5bxbek0bk.xn--p1ai"],
  }
})