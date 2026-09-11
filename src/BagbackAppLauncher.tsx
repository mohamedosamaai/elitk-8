import React, { useState, useEffect, useRef, useCallback } from "react";

export type EcosystemAppId = "ops" | "elitk" | "shop" | "mail" | "ai" | "core";

interface EcosystemApp {
  id: EcosystemAppId;
  label_en: string;
  label_ar: string;
  sub_en: string;
  sub_ar: string;
  url: string;
}

const ECOSYSTEM_APPS: EcosystemApp[] = [
  {
    id: "ops",
    label_en: "Ops ERP",
    label_ar: "نظام التشغيل",
    sub_en: "Flagship Operations",
    sub_ar: "العمليات الميدانية",
    url: "https://ops.bagbacktech.com",
  },
  {
    id: "elitk",
    label_en: "ELITK",
    label_ar: "إيليتك",
    sub_en: "Marketing & CRM",
    sub_ar: "التسويق وإدارة العملاء",
    url: "https://elitk.com",
  },
  {
    id: "shop",
    label_en: "Bagback Shop",
    label_ar: "متجر باج باك",
    sub_en: "Commerce & Procurement",
    sub_ar: "التجارة والمشتريات",
    url: "https://bagback.shop",
  },
  {
    id: "mail",
    label_en: "Mail Elitk",
    label_ar: "بريد إيليتك",
    sub_en: "Sovereign Communications",
    sub_ar: "البريد المؤسسي الآمن",
    url: "https://mail.elitk.com",
  },
  {
    id: "ai",
    label_en: "AI Workspace",
    label_ar: "مساحة الذكاء الاصطناعي",
    sub_en: "Developer & MCP Core",
    sub_ar: "المطورون وبروتوكول MCP",
    url: "https://ai.bagbacktech.com",
  },
  {
    id: "core",
    label_en: "BagbackTech",
    label_ar: "باج باك تك",
    sub_en: "Strategic Inception",
    sub_ar: "البوابة الاستراتيجية",
    url: "https://bagbacktech.com",
  },
];

function NineDotIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 18 18" fill="currentColor" aria-hidden="true" className={className}>
      <circle cx="2.5" cy="2.5" r="1.5" />
      <circle cx="9" cy="2.5" r="1.5" />
      <circle cx="15.5" cy="2.5" r="1.5" />
      <circle cx="2.5" cy="9" r="1.5" />
      <circle cx="9" cy="9" r="1.5" />
      <circle cx="15.5" cy="9" r="1.5" />
      <circle cx="2.5" cy="15.5" r="1.5" />
      <circle cx="9" cy="15.5" r="1.5" />
      <circle cx="15.5" cy="15.5" r="1.5" />
    </svg>
  );
}

export function BagbackAppLauncher({
  currentApp = "elitk",
  lang = "en",
}: {
  currentApp?: EcosystemAppId;
  lang?: "ar" | "en";
}) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const isAr = lang === "ar";

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!open) return;
    const onClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  const toggle = useCallback(() => setOpen((v) => !v), []);

  return (
    <div ref={containerRef} className="relative pointer-events-auto" dir={isAr ? "rtl" : "ltr"}>
      <button
        type="button"
        onClick={toggle}
        aria-expanded={open}
        aria-haspopup="true"
        aria-label="Open Bagback App Switcher"
        className="w-9 h-9 rounded-xl bg-black/40 backdrop-blur-3xl border border-white/10 text-white/70 hover:text-white hover:border-blue-500/50 hover:bg-blue-600/10 transition-all flex items-center justify-center cursor-pointer shadow-lg"
      >
        <NineDotIcon className="w-4 h-4" />
      </button>

      {open && (
        <div
          role="dialog"
          aria-modal="true"
          className="absolute top-full mt-2 end-0 w-72 bg-[#0a0d14]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden animate-in fade-in duration-150 text-start"
        >
          <div className="px-4 py-3 border-b border-white/5 bg-white/[0.02]">
            <p className="text-[10px] font-mono tracking-[0.14em] uppercase text-blue-400/80">
              {isAr ? "منظومة باج باك المؤسسية" : "BAGBACK ENTERPRISE SUITE"}
            </p>
          </div>

          <div className="p-3 grid grid-cols-2 gap-2">
            {ECOSYSTEM_APPS.map((app) => {
              const isActive = app.id === currentApp;
              return (
                <a
                  key={app.id}
                  href={app.url}
                  target={!isActive ? "_blank" : undefined}
                  rel={!isActive ? "noopener noreferrer" : undefined}
                  onClick={() => setOpen(false)}
                  className={`group flex flex-col gap-1.5 p-2.5 rounded-xl border transition-all ${
                    isActive
                      ? "border-blue-500/40 bg-blue-500/10 ring-1 ring-blue-500/20"
                      : "border-transparent hover:border-white/10 hover:bg-white/5"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[8px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-white/50 group-hover:text-blue-400">
                      {app.id.toUpperCase()}
                    </span>
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />}
                  </div>

                  <div className="min-w-0">
                    <p className={`text-xs font-bold leading-tight truncate ${isActive ? "text-blue-400" : "text-white"}`}>
                      {isAr ? app.label_ar : app.label_en}
                    </p>
                    <p className="text-[9px] text-white/40 leading-tight mt-0.5 truncate font-sans">
                      {isAr ? app.sub_ar : app.sub_en}
                    </p>
                  </div>
                </a>
              );
            })}
          </div>

          <div className="px-4 py-2 border-t border-white/5 bg-white/[0.01]">
            <p className="text-[9px] font-mono text-white/30 text-center">
              © 2026 BAGBACK DIGITAL SOLUTIONS
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
