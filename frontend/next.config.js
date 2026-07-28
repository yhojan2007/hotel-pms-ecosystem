/** @type {import('next').NextConfig} */
const apiInternalUrl = process.env.API_INTERNAL_URL || 'http://backend:8000';

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${apiInternalUrl}/api/v1/:path*`,
      },
    ]
  },
};

module.exports = nextConfig;
