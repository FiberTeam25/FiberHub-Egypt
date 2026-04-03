export type RFQStatus = "draft" | "open" | "closed" | "awarded" | "cancelled";
export type RFQResponseStatus = "invited" | "viewed" | "submitted" | "revised" | "withdrawn";

export interface RFQ {
  id: string;
  company_id: string;
  created_by: string;
  title: string;
  request_type: string | null;
  category_id: string | null;
  category_type: string | null;
  description: string | null;
  location: string | null;
  governorate: string | null;
  quantity_scope: string | null;
  timeline: string | null;
  deadline: string;
  notes: string | null;
  status: RFQStatus;
  awarded_to: string | null;
  created_at: string;
  updated_at: string;
  buyer_company_name?: string;
  attachments?: RFQAttachment[];
  invitations?: RFQInvitation[];
  response_count?: number;
}

export interface RFQAttachment {
  id: string;
  file_url: string;
  file_name: string;
  file_size: number | null;
}

export interface RFQInvitation {
  id: string;
  company_id: string;
  company_name?: string;
  status: RFQResponseStatus;
  invited_at: string;
  viewed_at: string | null;
}

export interface RFQResponse {
  id: string;
  rfq_id: string;
  company_id: string;
  submitted_by: string;
  cover_note: string | null;
  quoted_amount: number | null;
  currency: string | null;
  delivery_time: string | null;
  notes: string | null;
  file_url: string | null;
  file_name: string | null;
  status: RFQResponseStatus;
  submitted_at: string;
  company_name?: string;
}
