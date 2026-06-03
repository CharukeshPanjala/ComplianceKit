import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30, // 30 seconds — data stays fresh
      gcTime: 1000 * 60 * 5, // 5 minutes — cache kept in memory
      retry: 3, // retry failed requests 3 times
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000), // exponential backoff, max 30s
      refetchOnWindowFocus: true, // refresh when user returns to tab
      refetchOnReconnect: true, // refresh when internet reconnects
    },
    mutations: {
      retry: 1, // retry mutations once on failure
    },
  },
});
