"use client";

import { useNotifications, useMarkNotificationRead, useMarkAllRead } from "@/hooks/useNotifications";
import type { Notification, NotificationType } from "@/types/notification";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function notificationIcon(type: NotificationType): string {
  const icons: Record<NotificationType, string> = {
    email_verified: "M",
    verification_approved: "V",
    verification_rejected: "X",
    rfq_received: "R",
    rfq_response_submitted: "S",
    rfq_deadline_reminder: "D",
    new_message: "C",
    review_received: "W",
    account_suspended: "!",
  };
  return icons[type] ?? "N";
}

function notificationBadgeVariant(
  type: NotificationType,
): "default" | "secondary" | "destructive" | "outline" {
  switch (type) {
    case "verification_approved":
    case "email_verified":
      return "default";
    case "verification_rejected":
    case "account_suspended":
      return "destructive";
    case "rfq_received":
    case "rfq_response_submitted":
      return "secondary";
    default:
      return "outline";
  }
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function NotificationsPage() {
  const { data, isLoading, isError } = useNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllRead();

  const notifications: Notification[] = data?.items ?? data ?? [];

  const handleClick = (notification: Notification) => {
    if (!notification.is_read) {
      markRead.mutate(notification.id);
    }
    if (notification.link) {
      window.location.href = notification.link;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="py-20 text-center">
        <p className="text-destructive">Failed to load notifications.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Notifications</h1>
        {notifications.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
          >
            {markAllRead.isPending ? "Marking..." : "Mark All Read"}
          </Button>
        )}
      </div>

      {notifications.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">No notifications yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <Card
              key={n.id}
              className={`cursor-pointer transition-colors hover:bg-muted/50 ${
                !n.is_read ? "border-primary/30 bg-primary/5" : ""
              }`}
              onClick={() => handleClick(n)}
            >
              <CardContent className="flex items-start gap-4 py-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-bold">
                  {notificationIcon(n.type)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p
                      className={`text-sm truncate ${
                        !n.is_read ? "font-semibold" : "font-medium"
                      }`}
                    >
                      {n.title}
                    </p>
                    <Badge
                      variant={notificationBadgeVariant(n.type)}
                      className="shrink-0 text-xs"
                    >
                      {n.type.replace(/_/g, " ")}
                    </Badge>
                  </div>
                  {n.body && (
                    <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                      {n.body}
                    </p>
                  )}
                  <p className="mt-1 text-xs text-muted-foreground">
                    {timeAgo(n.created_at)}
                  </p>
                </div>
                {!n.is_read && (
                  <div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary" />
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
