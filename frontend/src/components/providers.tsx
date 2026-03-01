"use client";

import { SessionProvider } from "next-auth/react";
import { useRealtimeNotifications } from "@/hooks/useRealtimeNotifications";

function NotificationWrapper({ children }: { children: React.ReactNode }) {
  useRealtimeNotifications();
  return <>{children}</>;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <NotificationWrapper>
        {children}
      </NotificationWrapper>
    </SessionProvider>
  );
}
