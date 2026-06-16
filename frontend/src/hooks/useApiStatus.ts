import { useState, useEffect } from "react";
import { fetchHealth, fetchStats } from "../services/ragService";
import type { ApiStatus } from "../types/types";

interface UseApiStatusReturn {
  apiStatus:   ApiStatus;
  totalChunks: number | null;
}

export function useApiStatus(): UseApiStatusReturn {
  const [apiStatus,   setApiStatus]   = useState<ApiStatus>("checking");
  const [totalChunks, setTotalChunks] = useState<number | null>(null);

  useEffect(() => {
    fetchHealth().then(setApiStatus);
    fetchStats().then(setTotalChunks);
  }, []);

  return { apiStatus, totalChunks };
}