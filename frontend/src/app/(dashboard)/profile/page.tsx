"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuthStore } from "@/store/auth";
import { useTranslation } from "@/store/language";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

const GOVERNORATES = [
  "Cairo",
  "Giza",
  "Alexandria",
  "Qalyubia",
  "Dakahlia",
  "Sharqia",
  "Gharbia",
  "Monufia",
  "Beheira",
  "Kafr El Sheikh",
  "Damietta",
  "Port Said",
  "Ismailia",
  "Suez",
  "North Sinai",
  "South Sinai",
  "Fayoum",
  "Beni Suef",
  "Minya",
  "Asyut",
  "Sohag",
  "Qena",
  "Luxor",
  "Aswan",
  "Red Sea",
  "New Valley",
  "Matrouh",
];

interface ProfileForm {
  headline: string;
  bio: string;
  specializations: string[];
  experience_years: string;
  city: string;
  governorate: string;
  availability: string;
  hourly_rate: string;
}

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const t = useTranslation();
  const [profileId, setProfileId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [form, setForm] = useState<ProfileForm>({
    headline: "",
    bio: "",
    specializations: [],
    experience_years: "",
    city: "",
    governorate: "",
    availability: "available",
    hourly_rate: "",
  });

  const [tagInput, setTagInput] = useState("");

  useEffect(() => {
    api
      .get("/profiles/me")
      .then((res) => {
        const p = res.data;
        setProfileId(p.id);
        setForm({
          headline: p.headline ?? "",
          bio: p.bio ?? "",
          specializations: p.specializations ?? [],
          experience_years: p.experience_years?.toString() ?? "",
          city: p.city ?? "",
          governorate: p.governorate ?? "",
          availability: p.availability ?? "available",
          hourly_rate: p.hourly_rate?.toString() ?? "",
        });
      })
      .catch(() => setError(t("profile.loadFailed")))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = useCallback(
    (field: keyof ProfileForm, value: string | string[]) => {
      setForm((prev) => ({ ...prev, [field]: value }));
      setSaved(false);
    },
    [],
  );

  const addSpecialization = () => {
    const tag = tagInput.trim();
    if (tag && !form.specializations.includes(tag)) {
      handleChange("specializations", [...form.specializations, tag]);
      setTagInput("");
    }
  };

  const removeSpecialization = (tag: string) => {
    handleChange(
      "specializations",
      form.specializations.filter((s) => s !== tag),
    );
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        experience_years: form.experience_years
          ? parseInt(form.experience_years, 10)
          : null,
        hourly_rate: form.hourly_rate
          ? parseFloat(form.hourly_rate)
          : null,
      };
      if (profileId) {
        await api.patch(`/profiles/${profileId}`, payload);
      } else {
        const res = await api.post("/profiles", payload);
        setProfileId(res.data.id);
      }
      setSaved(true);
    } catch {
      setError(t("profile.saveFailed"));
    } finally {
      setSaving(false);
    }
  };

  if (user?.account_type !== "individual") {
    return (
      <div className="py-20 text-center">
        <p className="text-muted-foreground">
          Individual profiles are only available for individual accounts.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Edit Profile</h1>

      <Card>
        <CardHeader>
          <CardTitle>Professional Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="headline">Headline</Label>
            <Input
              id="headline"
              value={form.headline}
              onChange={(e) => handleChange("headline", e.target.value)}
              placeholder="e.g. Senior Fiber Optic Engineer"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="bio">Bio</Label>
            <Textarea
              id="bio"
              value={form.bio}
              onChange={(e) => handleChange("bio", e.target.value)}
              rows={4}
              placeholder="Describe your experience and expertise..."
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="experience">Experience (years)</Label>
            <Input
              id="experience"
              type="number"
              value={form.experience_years}
              onChange={(e) =>
                handleChange("experience_years", e.target.value)
              }
              placeholder="e.g. 10"
            />
          </div>
        </CardContent>
      </Card>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Specializations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              placeholder="Add a specialization..."
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addSpecialization();
                }
              }}
            />
            <Button variant="outline" onClick={addSpecialization} type="button">
              Add
            </Button>
          </div>
          {form.specializations.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {form.specializations.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeSpecialization(tag)}
                >
                  {tag} x
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Location &amp; Availability</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="city">City</Label>
              <Input
                id="city"
                value={form.city}
                onChange={(e) => handleChange("city", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Governorate</Label>
              <Select
                value={form.governorate}
                onValueChange={(v) => handleChange("governorate", v ?? "")}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select governorate" />
                </SelectTrigger>
                <SelectContent>
                  {GOVERNORATES.map((g) => (
                    <SelectItem key={g} value={g}>
                      {g}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Availability</Label>
              <Select
                value={form.availability}
                onValueChange={(v) => handleChange("availability", v ?? "available")}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Available</SelectItem>
                  <SelectItem value="busy">Busy</SelectItem>
                  <SelectItem value="not_available">Not Available</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="rate">Hourly Rate (EGP)</Label>
              <Input
                id="rate"
                type="number"
                value={form.hourly_rate}
                onChange={(e) => handleChange("hourly_rate", e.target.value)}
                placeholder="e.g. 500"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <p className="text-sm text-destructive">{error}</p>}
      {saved && (
        <p className="text-sm text-green-600">Profile saved successfully.</p>
      )}

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save Profile"}
        </Button>
      </div>
    </div>
  );
}
