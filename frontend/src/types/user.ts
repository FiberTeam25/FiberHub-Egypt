export type AccountType =
  | "buyer"
  | "supplier"
  | "distributor"
  | "manufacturer"
  | "contractor"
  | "subcontractor"
  | "individual"
  | "admin";

export type UserStatus = "active" | "suspended" | "deactivated";

export interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  phone: string | null;
  account_type: AccountType;
  status: UserStatus;
  email_verified: boolean;
  avatar_url: string | null;
  created_at: string;
}
