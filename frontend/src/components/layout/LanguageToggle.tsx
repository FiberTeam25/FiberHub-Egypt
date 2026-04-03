"use client";

import { useLanguageStore } from "@/store/language";
import { Button } from "@/components/ui/button";
import { Globe } from "lucide-react";

export function LanguageToggle() {
  const { lang, setLang } = useLanguageStore();

  const toggle = () => setLang(lang === "en" ? "ar" : "en");

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggle}
      className="gap-1.5 text-muted-foreground hover:text-foreground"
      title={lang === "en" ? "التبديل إلى العربية" : "Switch to English"}
    >
      <Globe className="h-4 w-4" />
      <span className="text-xs font-medium">{lang === "en" ? "AR" : "EN"}</span>
    </Button>
  );
}
