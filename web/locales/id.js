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
 * cOCR Workbench - Kamus Bahasa Indonesia
 *
 * Untuk menambahkan bahasa baru atau mengubah terjemahan, lihat web/locales/README.md
 */
(function (root) {
  const id = {
    meta: {
      code: "id",
      name: "Bahasa Indonesia",
      nativeName: "Bahasa Indonesia",
      direction: "ltr",
    },
    strings: {
      // Header & System Bar
      pageTitle: "cOCR Workbench - Ekstraksi & Restrukturisasi Dokumen",
      appTitle: "cOCR Workbench",
      appSubtitle: "Digitalisasi batch dokumen visual dan tangkapan layar ke Markdown, Word, dan PDF",
      systemStatusAria: "Status perangkat akselerasi",
      checkingDevice: "Memeriksa perangkat...",
      accelDevice: "Akselerasi: {device}",
      computeCpu: "Komputasi: CPU (Multi-Thread)",
      gpuNotFound: "GPU (Tidak Ditemukan)",
      systemOffline: "Sistem Offline",
      themeToggleAria: "Ganti mode tampilan terang atau gelap",
      themeToggleTitle: "Ganti mode tampilan",
      langToggleAria: "Pilih bahasa aplikasi",
      langToggleTitle: "Ganti bahasa",

      // Configuration Panel
      configTitle: "Pengaturan Pemrosesan",
      configSubtitle: "Pilih sumber berkas gambar dan tentukan format keluaran",
      imageSourceLabel: "Sumber Gambar",
      imageSourceCloudLabel: "Sumber Gambar (Mode Cloud: Unggah Berkas)",
      tabLocalFolder: "Folder Lokal",
      tabUploadFiles: "Unggah Berkas",
      folderPathLabel: "Lokasi Direktori Folder",
      folderPathPlaceholder: "Contoh: D:\\Dokumen\\Naskah_Scan",
      browseFolderBtn: "Pilih Folder",
      browseFolderAria: "Buka Explorer untuk memilih folder",
      browseFolderTitle: "Pilih folder berisi gambar",
      dropzoneAria: "Area drag and drop gambar",
      dropzoneTitle: "Tarik dan lepas gambar ke sini",
      dropzoneSubtitle: "atau klik untuk memilih berkas (.jpg, .png, .jpeg, .webp)",
      metaNoFilesSelected: "Belum ada berkas dipilih. Tentukan folder atau seret gambar ke area unggah.",
      metaCloudIsolated: "Mode Terisolasi: Unggah berkas gambar langsung ke area upload.",
      metaBrowsingFolder: "Membuka dialog pemilih folder...",
      metaDetectedFiles: "Terdeteksi {count} berkas gambar di folder ini.",
      metaNoImagesFound: "Tidak ada berkas gambar (.jpg, .jpeg, .png, .webp) pada folder yang dipilih.",
      metaFolderCancelled: "Pemilihan folder dibatalkan.",
      metaFolderFailed: "Gagal mengakses dialog folder.",
      metaFolderNotSpecified: "Lokasi folder belum ditentukan.",
      metaFolderInvalid: "Path direktori folder tidak valid.",
      metaFolderReady: "Terdeteksi {count} berkas gambar siap diproses.",
      metaFolderVerifyFailed: "Tidak dapat memverifikasi direktori folder.",
      metaUploadSingle: "Berkas Unggahan: {name} (1 gambar siap diproses).",
      metaUploadMultiple: "Sumber Unggahan: {count} berkas gambar siap diproses.",
      uploadStatusSingle: "Mengunggah berkas: {name}...",
      uploadStatusMultiple: "Mengunggah {count} berkas gambar...",
      uploadSuccessSingle: "Berhasil mengunggah 1 gambar: {name}. Siap diekstraksi.",
      uploadSuccessMultiple: "Berhasil mengunggah {count} gambar. Siap diekstraksi.",
      uploadFailed: "Gagal mengunggah berkas.",
      uploadError: "Gagal mengunggah gambar: {error}",

      // Form Controls
      outputFormatsLabel: "Format Dokumen Keluaran",
      chipTitleMd: "Format Dokumen Markdown (.md)",
      chipTitleDocx: "Format Dokumen Microsoft Word (.docx)",
      chipTitlePdf: "Format Dokumen PDF (.pdf)",
      accelDeviceLabel: "Perangkat Akselerasi",
      deviceSelectTitle: "Pilih perangkat akselerasi pemrosesan OCR",
      deviceOptionCpu: "CPU (Multi-Threading)",
      deviceOptionGpu: "GPU (CUDA / DirectML)",
      layoutModeLabel: "Format Tata Letak Dokumen",
      layoutSelectTitle: "Pilih mode tata letak dokumen",
      modeAuto: "Deteksi Otomatis (Tata Letak)",
      modeQuiz: "Tangkapan Layar Kuis (2 Kartu)",
      modeDocumentMcq: "Naskah Ujian & Pilihan Ganda",
      modeWorksheet: "Lembar Kerja Berseksi & Isian",
      modeFull: "Dokumen Bebas & Teks Penuh",
      outputDirLabel: "Folder Penyimpanan Hasil (Opsional)",
      outputDirPlaceholder: "Default: folder output di direktori sumber",
      btnStartExtraction: "Mulai Ekstraksi Dokumen",
      btnProcessing: "Memproses Gambar...",
      calloutTitle: "Penyaringan Watermark & Navigasi",
      calloutDesc: "Mendeteksi kotak miring watermark diagonal, menyaring nomor halaman bawah, dan mengecualikan tombol navigasi visual.",

      // Results Panel
      resultsTitle: "Pantauan & Hasil Ekstraksi",
      resultsSubtitle: "Pemantauan progres dan verifikasi naskah terstruktur",
      statusIdle: "Menunggu",
      statusProcessing: "Memproses",
      statusCompleted: "Selesai",
      statusError: "Kesalahan",
      errorBannerTitle: "Terjadi Kesalahan",
      dismissErrorAria: "Tutup pesan kesalahan",
      progressInitializing: "Menginisialisasi...",
      progressProcessing: "Sedang memproses OCR...",
      elapsedTimeLabel: "Waktu Berjalan:",
      metricTotalFiles: "Total Berkas",
      metricUniqueFiles: "Berkas Unik",
      metricDuplicates: "Duplikat Dilewati",
      metricDuration: "Total Durasi",
      downloadBarLabel: "Unduh Berkas Hasil:",
      tabPreview: "Pratinjau Butir Dokumen",
      tabMarkdown: "Dokumen Markdown",
      tabFiles: "Tabel Berkas",
      copyMarkdownBtn: "Salin Teks Markdown",
      copiedToClipboard: "Tersalin ke Clipboard!",
      thFilename: "Nama Berkas",
      thParsedPage: "Halaman Terbaca",
      thResolution: "Resolusi",
      thStatus: "Status",
      statusSuccess: "Sukses",
      statusSkipped: "Dilewati ({reason})",
      pageLabel: "Halaman {page}",
      pageNA: "N/A",
      emptyStateTitle: "Belum Ada Dokumen yang Diproses",
      emptyStateDesc: "Tentukan lokasi folder gambar atau unggah berkas dokumen pada panel konfigurasi di sebelah kiri, kemudian tekan tombol Mulai Ekstraksi Dokumen.",
      footerText: "cOCR Workbench. Pemrosesan dokumen visual dan tangkapan layar secara lokal di perangkat tanpa pengiriman data eksternal.",

      // Interactive & Error Dialogs
      apiKeyPrompt: "Server ini diproteksi oleh API Key (COCR_API_KEY). Silakan masukkan API Key Anda:",
      specifyFolderError: "Harap tentukan folder gambar atau unggah berkas gambar terlebih dahulu.",
      selectFormatError: "Pilih minimal satu format dokumen keluaran (Markdown, Word, atau PDF).",
      startOcrError: "Gagal memulai eksekusi OCR.",
      processFailedInternal: "Proses terhenti karena kegagalan internal.",
      noItemsExtracted: "Tidak ada butir dokumen yang berhasil diekstraksi.",
      textNotDetected: "Teks tidak terdeteksi.",
      itemNumberLabel: "Butir {item} (No. {number})",
      itemLabel: "Butir {item}",
      sectionHeader: "Bagian: {section}",
      instructionText: "({instruction})",

      // Markdown Preview Generation
      mdHeaderTitle: "# Hasil Ekstraksi Dokumen\n",
      mdExtractionTime: "Waktu Ekstraksi: {time}",
      mdTotalFilesSummary: "Total Berkas: {total} (Unik: {unique}, Duplikat: {duplicates})",
      mdOcrDevice: "Perangkat OCR: {device}\n",
      mdFileHeader: "## Berkas: `{filename}`",
      mdSectionHeader: "\n### Bagian: {section}",
      mdItemHeading: "#### {label} (Halaman {page})\n",
      mdItemPromptQuestion: "**Butir Pertanyaan:**\n> {text}\n",
      mdItemPromptContent: "**Konten Teks:**\n> {text}\n",
      mdOptionsHeader: "**Pilihan Jawaban:**",
    },
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = id;
  } else if (root.cocrI18n && typeof root.cocrI18n.registerLocale === "function") {
    root.cocrI18n.registerLocale(id);
  } else {
    root.COCR_LOCALES = root.COCR_LOCALES || {};
    root.COCR_LOCALES["id"] = id;
  }
})(typeof self !== "undefined" ? self : this);
