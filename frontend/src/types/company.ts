export type CompanyType =
  | "buyer"
  | "supplier"
  | "distributor"
  | "manufacturer"
  | "contractor"
  | "subcontractor";

export type VerificationStatus =
  | "not_submitted"
  | "pending"
  | "approved"
  | "rejected"
  | "expired"
  | "needs_update";

export type CompanySize = "1-10" | "11-50" | "51-200" | "201-500" | "500+";

export type MemberRole = "owner" | "admin" | "manager" | "member";

export interface Company {
  id: string;
  name: string;
  slug: string;
  company_type: CompanyType;
  description: string | null;
  logo_url: string | null;
  cover_url: string | null;
  website: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  governorate: string | null;
  company_size: CompanySize | null;
  year_established: number | null;
  commercial_reg_no: string | null;
  tax_id: string | null;
  verification_status: VerificationStatus;
  is_active: boolean;
  profile_completion: number;
  created_at: string;
  services?: CompanyService[];
  products?: CompanyProduct[];
  certifications?: Certification[];
  references?: ProjectReference[];
}

export interface CompanyService {
  id: string;
  service_category_id: string;
  description: string | null;
  category_name?: string;
}

export interface CompanyProduct {
  id: string;
  product_category_id: string;
  brand_names: string[] | null;
  description: string | null;
  category_name?: string;
}

export interface Certification {
  id: string;
  name: string;
  issuing_body: string | null;
  issue_date: string | null;
  expiry_date: string | null;
  document_url: string | null;
}

export interface ProjectReference {
  id: string;
  project_name: string;
  client_name: string | null;
  description: string | null;
  location: string | null;
  year: number | null;
  scope: string | null;
}

export interface CompanyMember {
  id: string;
  user_id: string;
  company_id: string;
  role: MemberRole;
  title: string | null;
  is_primary: boolean;
  first_name?: string | null;
  last_name?: string | null;
  email?: string;
}
