export type ReviewTargetType = "company" | "individual";

export interface Review {
  id: string;
  reviewer_id: string;
  reviewer_name: string | null;
  target_type: ReviewTargetType;
  target_company_id: string | null;
  target_profile_id: string | null;
  rfq_id: string | null;
  overall_rating: number;
  response_speed: number | null;
  communication: number | null;
  documentation: number | null;
  comment: string | null;
  is_visible: boolean;
  created_at: string;
  updated_at: string;
}
