import { create } from "zustand";
import { translations, type Locale, type TranslationKey } from "@/lib/i18n";

interface LanguageState {
  lang: Locale;
  setLang: (lang: Locale) => void;
  t: (key: TranslationKey) => string;
}

function getInitialLang(): Locale {
  if (typeof window === "undefined") return "en";
  const stored = localStorage.getItem("fiberhub-lang");
  if (stored === "ar" || stored === "en") return stored;
  return "en";
}

function applyLangToDocument(lang: Locale) {
  if (typeof document === "undefined") return;
  const html = document.documentElement;
  html.setAttribute("lang", lang);
  html.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");

  // Toggle the Arabic font class on <body>
  if (lang === "ar") {
    document.body.classList.add("font-arabic");
  } else {
    document.body.classList.remove("font-arabic");
  }
}

export const useLanguageStore = create<LanguageState>((set, get) => {
  // Apply initial language on store creation (client-side only)
  const initial = getInitialLang();
  if (typeof window !== "undefined") {
    // Defer to avoid SSR hydration issues
    queueMicrotask(() => applyLangToDocument(initial));
  }

  return {
    lang: initial,

    setLang: (lang) => {
      localStorage.setItem("fiberhub-lang", lang);
      applyLangToDocument(lang);
      set({ lang });
    },

    t: (key) => {
      const lang = get().lang;
      return translations[lang][key] ?? key;
    },
  };
});
