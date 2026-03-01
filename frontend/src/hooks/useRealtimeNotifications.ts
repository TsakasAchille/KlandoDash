"use client";

import { useEffect } from "react";
import { supabase } from "@/lib/supabase";
import { useSession } from "next-auth/react";
import { toast } from "sonner";

/**
 * Hook to handle desktop and toast notifications for the entire dashboard.
 */
export function useRealtimeNotifications() {
  const { data: session } = useSession();

  useEffect(() => {
    if (!session?.user?.email) return;

    // 1. Request Permission
    if (typeof window !== "undefined" && "Notification" in window) {
      if (Notification.permission === "default") {
        Notification.requestPermission();
      }
    }

    // 2. Setup Subscriptions
    const setupSubscriptions = () => {
      // --- Channel: Support Tickets ---
      const ticketChannel = supabase
        .channel('realtime_support')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'support_tickets' },
          (payload) => {
            const ticket = payload.new;
            showNotification(
              "Nouveau Ticket Support",
              `Un nouveau ticket a été créé : ${ticket.subject || 'Sans sujet'}`
            );
          }
        )
        .subscribe();

      // --- Channel: Internal Chat ---
      const chatChannel = supabase
        .channel('realtime_chat')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'dash_internal_messages' },
          (payload) => {
            const msg = payload.new;
            // Don't notify if I am the sender
            if (msg.sender_email !== session.user.email) {
              showNotification(
                "Nouveau message d'équipe",
                msg.content.substring(0, 100) + (msg.content.length > 100 ? '...' : '')
              );
            }
          }
        )
        .subscribe();

      return () => {
        supabase.removeChannel(ticketChannel);
        supabase.removeChannel(chatChannel);
      };
    };

    const cleanup = setupSubscriptions();
    return () => cleanup();
  }, [session]);

  const showNotification = (title: string, body: string) => {
    // A. Native Desktop Notification
    if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "granted") {
      new Notification(title, {
        body,
        icon: "/icon.png"
      });
    }

    // B. Dashboard Toast (Fallback or concurrent)
    toast.info(title, {
      description: body,
      duration: 5000,
    });
  };
}
