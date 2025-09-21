/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:{{cookiecutter.backend_port}}',
    {% if cookiecutter.use_websockets == "yes" %}
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:{{cookiecutter.backend_port}}',
    {% endif %}
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:{{cookiecutter.backend_port}}'}/api/:path*`,
      },
    ]
  },
  output: 'standalone',
  experimental: {
    // Enable if using app directory (Next.js 13+)
    appDir: false,
  },
}

module.exports = nextConfig
