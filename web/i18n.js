/*
 * cOCR Workbench
 *
 * Copyright (C) 2026 Dika Ardianta
 * Copyright (C) 2026 Hisoka Labs
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License
 * as published by the Free Software Foundation, either version 3
 * of the License, or (at your option) any later version.
 *
 * See LICENSE for details.
 */

/**
 * cOCR Workbench - Internationalization (i18n) Engine
 *
 * Lightweight, offline-ready localization engine with accessibility,
 * keyboard navigation, and automatic DOM translation bindings.
 */
(function (root) {
  "use strict";

  const DEFAULT_LANG = "en";
  const STORAGE_KEY = "cocr_lang";

  const locales = {};
  let currentLang = DEFAULT_LANG;
  let isInitialized = false;

  // Determine initial language from localStorage or fallback to English
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && typeof saved === "string") {
      currentLang = saved.toLowerCase().trim();
    }
  } catch (_) {
    currentLang = DEFAULT_LANG;
  }

  // Absorb any locales loaded before i18n.js
  if (root.COCR_LOCALES) {
    Object.keys(root.COCR_LOCALES).forEach((code) => {
      locales[code] = root.COCR_LOCALES[code];
    });
  }

  /**
   * Register a locale dictionary object.
   * Format: { meta: { code, name, nativeName, direction }, strings: { ... } }
   */
  function registerLocale(locale) {
    if (!locale || !locale.meta || !locale.meta.code) {
      console.warn("[i18n] Invalid locale object rejected:", locale);
      return;
    }
    const code = locale.meta.code.toLowerCase().trim();
    locales[code] = locale;

    if (isInitialized) {
      renderLanguageMenu();
    }
  }

  /**
   * Return an array of all registered locale metadata objects.
   */
  function getAvailableLocales() {
    return Object.keys(locales).map((code) => locales[code].meta);
  }

  /**
   * Return current active language code.
   */
  function getCurrentLanguage() {
    return currentLang;
  }

  /**
   * Translate a key with optional dynamic parameter interpolation.
   * Falls back to English if the key is missing in the current locale.
   */
  function t(key, params) {
    if (!key) return "";

    const activeDict = locales[currentLang] && locales[currentLang].strings;
    const fallbackDict = locales[DEFAULT_LANG] && locales[DEFAULT_LANG].strings;

    let text = (activeDict && activeDict[key]) !== undefined
      ? activeDict[key]
      : (fallbackDict && fallbackDict[key]) !== undefined
        ? fallbackDict[key]
        : key;

    if (params && typeof params === "object") {
      Object.keys(params).forEach((paramKey) => {
        const val = params[paramKey] !== undefined && params[paramKey] !== null ? params[paramKey] : "";
        text = text.replace(new RegExp(`\\{${paramKey}\\}`, "g"), String(val));
      });
    }

    return text;
  }

  /**
   * Apply translations to all matching DOM elements in the document or container.
   */
  function applyTranslations(container) {
    const rootEl = container || document;

    // Document-level attributes
    if (rootEl === document) {
      const activeMeta = locales[currentLang] && locales[currentLang].meta;
      document.documentElement.lang = currentLang;
      document.documentElement.dir = (activeMeta && activeMeta.direction) || "ltr";

      const titleKey = "pageTitle";
      const translatedTitle = t(titleKey);
      if (translatedTitle && translatedTitle !== titleKey) {
        document.title = translatedTitle;
      }
    }

    // Text content: [data-i18n="key"]
    const textElements = rootEl.querySelectorAll("[data-i18n]");
    textElements.forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!key) return;
      if (el.hasAttribute("data-i18n-html")) {
        el.innerHTML = t(key);
      } else {
        el.textContent = t(key);
      }
    });

    // Attributes: [data-i18n-attr="attr1:key1,attr2:key2"]
    const attrElements = rootEl.querySelectorAll("[data-i18n-attr]");
    attrElements.forEach((el) => {
      const spec = el.getAttribute("data-i18n-attr");
      if (!spec) return;
      const pairs = spec.split(",");
      pairs.forEach((pair) => {
        const parts = pair.split(":");
        if (parts.length === 2) {
          const attr = parts[0].trim();
          const key = parts[1].trim();
          if (attr && key) {
            el.setAttribute(attr, t(key));
          }
        }
      });
    });

    // Update Language Trigger Button label and accessibility
    updateLanguageTrigger();
  }

  /**
   * Set active language and re-render translations across the interface.
   */
  function setLanguage(langCode) {
    const target = (langCode || "").toLowerCase().trim();
    if (!locales[target]) {
      console.warn(`[i18n] Requested locale '${target}' not found. Falling back to '${DEFAULT_LANG}'.`);
      currentLang = locales[DEFAULT_LANG] ? DEFAULT_LANG : Object.keys(locales)[0] || DEFAULT_LANG;
    } else {
      currentLang = target;
    }

    try {
      localStorage.setItem(STORAGE_KEY, currentLang);
    } catch (_) {}

    applyTranslations();
    renderLanguageMenu();

    // Dispatch global event for application-specific reactive updates
    const event = new CustomEvent("cocr:languageChange", {
      detail: {
        lang: currentLang,
        locale: locales[currentLang] || null,
        t: t,
      },
    });
    window.dispatchEvent(event);
    document.dispatchEvent(event);
  }

  /**
   * Update the UI language trigger button text and ARIA state.
   */
  function updateLanguageTrigger() {
    const codeSpan = document.getElementById("current-lang-code");
    if (codeSpan) {
      codeSpan.textContent = currentLang.toUpperCase();
    }

    const btnToggle = document.getElementById("btn-lang-toggle");
    if (btnToggle) {
      const activeMeta = locales[currentLang] && locales[currentLang].meta;
      const langName = activeMeta ? activeMeta.name : currentLang.toUpperCase();
      const ariaLabel = `${t("langToggleAria")} (${langName})`;
      btnToggle.setAttribute("aria-label", ariaLabel);
      btnToggle.setAttribute("title", t("langToggleTitle"));
    }
  }

  /**
   * Render the language selection dropdown menu options.
   */
  function renderLanguageMenu() {
    const menu = document.getElementById("lang-dropdown-menu");
    if (!menu) return;

    menu.innerHTML = "";
    const available = getAvailableLocales();

    // If no locales loaded yet, show fallback
    if (available.length === 0) {
      available.push({ code: "en", name: "English" }, { code: "id", name: "Bahasa Indonesia" });
    }

    available.forEach((loc) => {
      const li = document.createElement("li");
      li.setAttribute("role", "option");
      li.setAttribute("data-lang", loc.code);
      li.className = `lang-option${loc.code === currentLang ? " active" : ""}`;
      li.setAttribute("aria-selected", loc.code === currentLang ? "true" : "false");
      li.setAttribute("tabindex", loc.code === currentLang ? "0" : "-1");

      const nameSpan = document.createElement("span");
      nameSpan.className = "lang-name";
      nameSpan.textContent = loc.name || loc.code.toUpperCase();

      const badgeSpan = document.createElement("span");
      badgeSpan.className = "lang-option-badge";
      badgeSpan.textContent = loc.code.toUpperCase();

      li.appendChild(nameSpan);
      li.appendChild(badgeSpan);

      li.addEventListener("click", () => {
        setLanguage(loc.code);
        closeLanguageMenu();
        const btnToggle = document.getElementById("btn-lang-toggle");
        if (btnToggle) btnToggle.focus();
      });

      li.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          setLanguage(loc.code);
          closeLanguageMenu();
          const btnToggle = document.getElementById("btn-lang-toggle");
          if (btnToggle) btnToggle.focus();
        }
      });

      menu.appendChild(li);
    });

    updateLanguageTrigger();
  }

  function openLanguageMenu() {
    const btn = document.getElementById("btn-lang-toggle");
    const menu = document.getElementById("lang-dropdown-menu");
    if (!btn || !menu) return;

    btn.setAttribute("aria-expanded", "true");
    menu.removeAttribute("hidden");

    // Focus active option or first option
    const activeOption = menu.querySelector(".lang-option.active") || menu.querySelector(".lang-option");
    if (activeOption) {
      setTimeout(() => activeOption.focus(), 20);
    }
  }

  function closeLanguageMenu() {
    const btn = document.getElementById("btn-lang-toggle");
    const menu = document.getElementById("lang-dropdown-menu");
    if (!btn || !menu) return;

    btn.setAttribute("aria-expanded", "false");
    menu.setAttribute("hidden", "");
  }

  function toggleLanguageMenu() {
    const btn = document.getElementById("btn-lang-toggle");
    if (!btn) return;
    const isExpanded = btn.getAttribute("aria-expanded") === "true";
    if (isExpanded) {
      closeLanguageMenu();
    } else {
      openLanguageMenu();
    }
  }

  /**
   * Setup keyboard navigation and outside-click listeners for the language dropdown.
   */
  function setupLanguageMenuEvents() {
    const wrapper = document.getElementById("lang-selector-wrapper");
    const btn = document.getElementById("btn-lang-toggle");
    const menu = document.getElementById("lang-dropdown-menu");

    if (!btn || !menu) return;

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleLanguageMenu();
    });

    // Close on outside click
    document.addEventListener("click", (e) => {
      if (wrapper && !wrapper.contains(e.target)) {
        closeLanguageMenu();
      }
    });

    // Close on Escape, navigate with Arrow keys
    wrapper.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeLanguageMenu();
        btn.focus();
        return;
      }

      const options = Array.from(menu.querySelectorAll(".lang-option"));
      if (options.length === 0) return;
      const currentIndex = options.indexOf(document.activeElement);

      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (btn.getAttribute("aria-expanded") !== "true") {
          openLanguageMenu();
          return;
        }
        const nextIndex = (currentIndex + 1) % options.length;
        options[nextIndex].focus();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (btn.getAttribute("aria-expanded") !== "true") {
          openLanguageMenu();
          return;
        }
        const prevIndex = (currentIndex - 1 + options.length) % options.length;
        options[prevIndex].focus();
      } else if (e.key === "Home") {
        e.preventDefault();
        options[0].focus();
      } else if (e.key === "End") {
        e.preventDefault();
        options[options.length - 1].focus();
      }
    });
  }

  /**
   * Initialization once DOM is ready.
   */
  function init() {
    if (isInitialized) return;
    isInitialized = true;

    // Verify current language exists, fallback to default
    if (!locales[currentLang]) {
      currentLang = locales[DEFAULT_LANG] ? DEFAULT_LANG : Object.keys(locales)[0] || DEFAULT_LANG;
    }

    renderLanguageMenu();
    setupLanguageMenuEvents();
    applyTranslations();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Export public API
  const api = {
    registerLocale: registerLocale,
    getAvailableLocales: getAvailableLocales,
    getCurrentLanguage: getCurrentLanguage,
    setLanguage: setLanguage,
    t: t,
    applyTranslations: applyTranslations,
    DEFAULT_LANG: DEFAULT_LANG,
  };

  root.cocrI18n = api;
})(typeof self !== "undefined" ? self : this);
