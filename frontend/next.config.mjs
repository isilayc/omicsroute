const nextConfig = {
  // The planner is a client application; FastAPI handles all server work.
  output: "export",
  // Production always uses the backend in this Vercel deployment.
  // This also overrides a stale NEXT_PUBLIC_OMICSROUTE_API_URL in the dashboard.
  env: {
    NEXT_PUBLIC_OMICSROUTE_API_URL:
      process.env.NODE_ENV === "production"
        ? ""
        : process.env.NEXT_PUBLIC_OMICSROUTE_API_URL || "http://127.0.0.1:8000",
  },
};

export default nextConfig;
