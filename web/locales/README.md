# Internationalization (i18n) & Localization Guide

cOCR Workbench supports multi-language interfaces through a lightweight, offline-first localization architecture. This guide explains how translations work and how to add a new language.

---

## Supported Locales

- **English (`en`)**: Default language. Defined in [`en.js`](en.js).
- **Bahasa Indonesia (`id`)**: Indonesian localization. Defined in [`id.js`](id.js).

---

## How Translations Work

1. Each language dictionary lives in its own file under `web/locales/<language-code>.js`.
2. Locales register with the global i18n controller (`cocrI18n`) on load.
3. If a translation key is missing in a non-default language, the engine falls back to English automatically.
4. User language preference is stored in `localStorage` under `cocr_lang`.

---

## Adding a New Language in 3 Steps

### Step 1: Duplicate the English Template

Copy `web/locales/en.js` and rename it to your target ISO 639-1 language code (for example, `es.js` for Spanish, `de.js` for German, `ja.js` for Japanese, or `fr.js` for French):

```bash
cp web/locales/en.js web/locales/es.js
```

### Step 2: Translate the Strings

Open the newly created file and update the `meta` block and string values:

```javascript
(function (root) {
  const es = {
    meta: {
      code: "es",
      name: "Español",
      nativeName: "Español",
      direction: "ltr",
    },
    strings: {
      pageTitle: "cOCR Workbench - Extracción y Reestructuración de Documentos",
      appTitle: "cOCR Workbench",
      appSubtitle: "Digitalización por lotes de documentos visuales a Markdown, Word y PDF",
      // ... translate remaining string values here ...
    },
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = es;
  } else if (root.cocrI18n && typeof root.cocrI18n.registerLocale === "function") {
    root.cocrI18n.registerLocale(es);
  } else {
    root.COCR_LOCALES = root.COCR_LOCALES || {};
    root.COCR_LOCALES["es"] = es;
  }
})(typeof self !== "undefined" ? self : this);
```

### Step 3: Register the Script in `web/index.html`

Open `web/index.html` and add the script tag right next to the existing locale scripts:

```html
<script src="/static/locales/en.js"></script>
<script src="/static/locales/id.js"></script>
<script src="/static/locales/es.js"></script> <!-- Your new locale -->
<script src="/static/app.js"></script>
```

That is it. The language dropdown in the top navigation bar will automatically discover the registered locale and list it for users.

---

## Translation Guidelines

- **Keep placeholders intact**: Placeholders such as `{count}`, `{name}`, `{device}`, `{time}`, and `{error}` are dynamically interpolated at runtime. Do not alter their names.
- **Maintain tone and clarity**: Translations should be direct, factual, and accessible. Avoid unnecessary jargon or slang.
- **Preserve format identifiers**: Technical terms like Markdown, Word (.docx), PDF (.pdf), ONNX, CPU, and GPU should remain recognizable across languages.
