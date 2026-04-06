"use client";

import { useEffect, useState, useCallback } from "react";
import api from "@/lib/api";
import { useTranslation } from "@/store/language";
import { NoCompanyPrompt } from "@/components/layout/NoCompanyPrompt";
import type { CompanyMember, MemberRole } from "@/types/company";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const ROLES: MemberRole[] = ["owner", "admin", "manager", "member"];

export default function TeamPage() {
  const t = useTranslation();
  const [companyId, setCompanyId] = useState<string | null>(null);
  const [members, setMembers] = useState<CompanyMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add member dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<MemberRole>("member");
  const [inviting, setInviting] = useState(false);

  const fetchMembers = useCallback(async (cId: string) => {
    try {
      const res = await api.get(`/companies/${cId}/members`);
      setMembers(res.data.items ?? res.data);
    } catch {
      setError(t("company.teamLoadFailed"));
    }
  }, []);

  useEffect(() => {
    api
      .get("/companies/mine")
      .then(async (res) => {
        const cId = res.data.id;
        setCompanyId(cId);
        await fetchMembers(cId);
      })
      .catch(() => setError(t("company.companyLoadFailed")))
      .finally(() => setLoading(false));
  }, [fetchMembers]);

  const handleInvite = async () => {
    if (!companyId || !inviteEmail.trim()) return;
    setInviting(true);
    try {
      await api.post(`/companies/${companyId}/members`, {
        email: inviteEmail.trim(),
        role: inviteRole,
      });
      setDialogOpen(false);
      setInviteEmail("");
      setInviteRole("member");
      await fetchMembers(companyId);
    } catch {
      setError(t("company.addMemberFailed"));
    } finally {
      setInviting(false);
    }
  };

  const handleRoleChange = async (memberId: string, role: MemberRole) => {
    if (!companyId) return;
    try {
      await api.patch(`/companies/${companyId}/members/${memberId}`, { role });
      await fetchMembers(companyId);
    } catch {
      setError(t("company.updateRoleFailed"));
    }
  };

  const handleRemove = async (memberId: string) => {
    if (!companyId) return;
    if (!confirm("Are you sure you want to remove this member?")) return;
    try {
      await api.delete(`/companies/${companyId}/members/${memberId}`);
      await fetchMembers(companyId);
    } catch {
      setError(t("company.removeMemberFailed"));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error && !companyId) {
    return <NoCompanyPrompt />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Team Members</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger render={<Button />}>
            Add Member
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Team Member</DialogTitle>
              <DialogDescription>
                Invite a user by email to join your company.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="invite-email">Email Address</Label>
                <Input
                  id="invite-email"
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="user@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Select
                  value={inviteRole}
                  onValueChange={(v) => setInviteRole((v ?? "member") as MemberRole)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES.map((r) => (
                      <SelectItem key={r} value={r}>
                        {r.charAt(0).toUpperCase() + r.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button onClick={handleInvite} disabled={inviting}>
                {inviting ? "Adding..." : "Add Member"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Card>
        <CardHeader>
          <CardTitle>Members ({members.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {members.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No team members yet.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell className="font-medium">
                      {[m.first_name, m.last_name].filter(Boolean).join(" ") ||
                        "—"}
                    </TableCell>
                    <TableCell>{m.email ?? "—"}</TableCell>
                    <TableCell>
                      <Select
                        value={m.role}
                        onValueChange={(v: string | null) =>
                          handleRoleChange(m.id, v as MemberRole)
                        }
                      >
                        <SelectTrigger className="w-[120px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {ROLES.map((r) => (
                            <SelectItem key={r} value={r}>
                              {r.charAt(0).toUpperCase() + r.slice(1)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {m.is_primary ? "Primary" : "Member"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {!m.is_primary && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-destructive hover:text-destructive"
                          onClick={() => handleRemove(m.id)}
                        >
                          Remove
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
