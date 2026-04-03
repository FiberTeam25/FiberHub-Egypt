import { create } from "zustand";
import { translations, type Locale, type TranslationKey } from "@/lib/i18n";

interface LanguageState {
  lang: Locale;
  setLang: (lang: Locale) => void;
  hydrate: () => void;
}

function applyLangToDocument(lang: Locale) {
  if (typeof document === "undefined") return;
  const html = document.documentElement;
  html.setAttribute("lang", lang);
  html.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");

  if (lang === "ar") {
    document.body.classList.add("font-arabic");
  } else {
    document.body.classList.remove("font-arabic");
  }
}

export const useLanguageStore = create<LanguageState>((set) => ({
  lang: "en",

  setLang: (lang) => {
    localStorage.setItem("fiberhub-lang", lang);
    applyLangToDocument(lang);
    set({ lang });
  },

  hydrate: () => {
    if (typeof window === "undefined") return;
    const stored = localStorage.getItem("fiberhub-lang");
    const lang: Locale = stored === "ar" ? "ar" : "en";
    applyLangToDocument(lang);
    set({ lang });
  },
}));

/** Hook that returns a translation function and re-renders when language changes */
export function useTranslation() {
  const lang = useLanguageStore((s) => s.lang);
  return (key: TranslationKey): string => translations[lang][key] ?? key;
}
