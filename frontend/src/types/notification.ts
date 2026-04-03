export type NotificationType =
  | "email_verified"
  | "verification_approved"
  | "verification_rejected"
  | "rfq_received"
  | "rfq_response_submitted"
  | "rfq_deadline_reminder"
  | "new_message"
  | "review_received"
  | "account_suspended";

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  body: string | null;
  link: string | null;
  is_read: boolean;
  created_at: string;
}
