/**
 * Custom hook for WebSocket connection to receive training status updates.
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import type { TrainingStatus } from '@/types';

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export interface UseWebSocketReturn {
  /** Current training status */
  status: TrainingStatus | null;
  /** Whether the WebSocket is connected */
  isConnected: boolean;
  /** Connect to training status updates */
  connect: (profileId: string) => void;
  /** Disconnect from updates */
  disconnect: () => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const [status, setStatus] = useState<TrainingStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    setIsConnected(false);
  }, []);

  const connect = useCallback(
    (profileId: string) => {
      disconnect();

      const ws = new WebSocket(`${WS_BASE}/training/${profileId}`);

      ws.onopen = () => {
        setIsConnected(true);
        console.log(`WebSocket connected for profile ${profileId}`);
      };

      ws.onmessage = (event) => {
        try {
          const data: TrainingStatus = JSON.parse(event.data);
          setStatus(data);

          // Auto-close on completion or failure
          if (data.status === 'ready' || data.status === 'failed') {
            setTimeout(() => disconnect(), 2000);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Auto-reconnect for training status (not if completed)
        if (status?.status !== 'ready' && status?.status !== 'failed') {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect(profileId);
          }, 3000);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      wsRef.current = ws;
    },
    [disconnect, status?.status],
  );

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return { status, isConnected, connect, disconnect };
}
