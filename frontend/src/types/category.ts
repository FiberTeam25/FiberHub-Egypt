export interface Category {
  id: string;
  name: string;
  slug: string;
  parent_id: string | null;
  description: string | null;
  icon: string | null;
  sort_order: number;
  is_active: boolean;
  children?: Category[];
}

export interface Governorate {
  id: string;
  name: string;
  name_ar: string | null;
}
