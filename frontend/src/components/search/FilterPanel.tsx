"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Governorate } from "@/types/category";

const companyTypes = [
  { value: "buyer", label: "Buyer" },
  { value: "supplier", label: "Supplier" },
  { value: "distributor", label: "Distributor" },
  { value: "manufacturer", label: "Manufacturer" },
  { value: "contractor", label: "Contractor" },
  { value: "subcontractor", label: "Subcontractor" },
];

interface FilterPanelProps {
  filters: Record<string, string | boolean | undefined>;
  governorates: Governorate[];
  onFilterChange: (f: Record<string, string | boolean | undefined>) => void;
}

export function FilterPanel({ filters, governorates, onFilterChange }: FilterPanelProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>Company Type</Label>
        <Select value={(filters.company_type as string) || ""} onValueChange={(v) => onFilterChange({ ...filters, company_type: v || undefined })}>
          <SelectTrigger><SelectValue placeholder="All types" /></SelectTrigger>
          <SelectContent>
            {companyTypes.map((t) => (<SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Governorate</Label>
        <Select value={(filters.governorate as string) || ""} onValueChange={(v) => onFilterChange({ ...filters, governorate: v || undefined })}>
          <SelectTrigger><SelectValue placeholder="All governorates" /></SelectTrigger>
          <SelectContent>
            {governorates.map((g) => (<SelectItem key={g.id} value={g.name}>{g.name}</SelectItem>))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" id="verified" checked={!!filters.verified_only} onChange={(e) => onFilterChange({ ...filters, verified_only: e.target.checked || undefined })} className="rounded border-input" />
        <Label htmlFor="verified" className="text-sm font-normal cursor-pointer">Verified only</Label>
      </div>
      <Button variant="ghost" size="sm" className="w-full" onClick={() => onFilterChange({})}>Clear Filters</Button>
    </div>
  );
}
