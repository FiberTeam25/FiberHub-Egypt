export type ThreadContextType = "direct" | "rfq" | "support";

export interface MessageThread {
  id: string;
  context_type: ThreadContextType;
  context_id: string | null;
  subject: string | null;
  created_at: string;
  updated_at: string;
  last_message?: string | null;
  unread_count?: number;
  participants?: ThreadParticipant[];
}

export interface ThreadParticipant {
  id: string;
  user_id: string;
  company_id: string | null;
  first_name?: string | null;
  last_name?: string | null;
}

export interface Message {
  id: string;
  thread_id: string;
  sender_id: string;
  content: string;
  created_at: string;
  sender_name?: string;
  attachments?: MessageAttachment[];
}

export interface MessageAttachment {
  id: string;
  file_url: string;
  file_name: string;
  file_size: number | null;
}
