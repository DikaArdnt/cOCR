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
 * cOCR Workbench - English Locale Dictionary (Default)
 *
 * To contribute a new language or modify translations, see web/locales/README.md
 */
(function (root) {
  const en = {
    meta: {
      code: "en",
      name: "English",
      nativeName: "English",
      direction: "ltr",
    },
    strings: {
      // Header & System Bar
      pageTitle: "cOCR Workbench - Document Extraction & Restructuring",
      appTitle: "cOCR Workbench",
      appSubtitle: "Batch digitize visual documents and screenshots into Markdown, Word, and PDF",
      systemStatusAria: "Hardware acceleration status",
      checkingDevice: "Checking device...",
      accelDevice: "Acceleration: {device}",
      computeCpu: "Compute: CPU (Multi-Thread)",
      gpuNotFound: "GPU (Not Detected)",
      systemOffline: "System Offline",
      themeToggleAria: "Switch light or dark display mode",
      themeToggleTitle: "Switch display mode",
      langToggleAria: "Select application language",
      langToggleTitle: "Change language",

      // Configuration Panel
      configTitle: "Processing Configuration",
      configSubtitle: "Select document images and specify output formats",
      imageSourceLabel: "Image Source",
      imageSourceCloudLabel: "Image Source (Cloud Mode: File Upload)",
      tabLocalFolder: "Local Folder",
      tabUploadFiles: "Upload Files",
      folderPathLabel: "Folder Directory Path",
      folderPathPlaceholder: "e.g. D:\\Documents\\Scanned_Docs",
      browseFolderBtn: "Browse Folder",
      browseFolderAria: "Open dialog to select folder",
      browseFolderTitle: "Select folder containing images",
      dropzoneAria: "Image drag and drop area",
      dropzoneTitle: "Drag and drop images here",
      dropzoneSubtitle: "or click to browse files (.jpg, .png, .jpeg, .webp)",
      metaNoFilesSelected: "No files selected. Specify a folder or drag images to the upload area.",
      metaCloudIsolated: "Isolated Mode: Upload image files directly to the drop zone.",
      metaBrowsingFolder: "Opening folder selection dialog...",
      metaDetectedFiles: "Detected {count} image files in this folder.",
      metaNoImagesFound: "No image files (.jpg, .jpeg, .png, .webp) found in the selected folder.",
      metaFolderCancelled: "Folder selection was cancelled.",
      metaFolderFailed: "Failed to access folder dialog.",
      metaFolderNotSpecified: "Folder directory has not been specified.",
      metaFolderInvalid: "Folder directory path is invalid.",
      metaFolderReady: "Detected {count} image files ready for processing.",
      metaFolderVerifyFailed: "Unable to verify folder directory.",
      metaUploadSingle: "Uploaded File: {name} (1 image ready to process).",
      metaUploadMultiple: "Uploaded Source: {count} image files ready to process.",
      uploadStatusSingle: "Uploading file: {name}...",
      uploadStatusMultiple: "Uploading {count} image files...",
      uploadSuccessSingle: "Successfully uploaded 1 image: {name}. Ready for extraction.",
      uploadSuccessMultiple: "Successfully uploaded {count} images. Ready for extraction.",
      uploadFailed: "Failed to upload files.",
      uploadError: "Failed to upload images: {error}",

      // Form Controls
      outputFormatsLabel: "Output Document Formats",
      chipTitleMd: "Markdown Document Format (.md)",
      chipTitleDocx: "Microsoft Word Document Format (.docx)",
      chipTitlePdf: "PDF Document Format (.pdf)",
      accelDeviceLabel: "Acceleration Device",
      deviceSelectTitle: "Select OCR processing acceleration device",
      deviceOptionCpu: "CPU (Multi-Threading)",
      deviceOptionGpu: "GPU (CUDA / DirectML)",
      layoutModeLabel: "Document Layout Mode",
      layoutSelectTitle: "Select document layout mode",
      modeAuto: "Auto Detect (Document Layout)",
      modeQuiz: "Quiz Screenshot (2-Card Split)",
      modeDocumentMcq: "Exam Paper & Multiple Choice",
      modeWorksheet: "Sectioned Worksheet & Fill-ins",
      modeFull: "Freeform Document & Full Text",
      outputDirLabel: "Output Destination Folder (Optional)",
      outputDirPlaceholder: "Default: output folder inside source directory",
      btnStartExtraction: "Start Document Extraction",
      btnProcessing: "Processing Images...",
      calloutTitle: "Watermark & Navigation Filtering",
      calloutDesc: "Detects angled diagonal watermarks, filters footer page numbers, and excludes on-screen navigation elements.",

      // Results Panel
      resultsTitle: "Monitoring & Extracted Results",
      resultsSubtitle: "Progress monitoring and structured document verification",
      statusIdle: "Idle",
      statusProcessing: "Processing",
      statusCompleted: "Completed",
      statusError: "Error",
      errorBannerTitle: "An Error Occurred",
      dismissErrorAria: "Dismiss error message",
      progressInitializing: "Initializing...",
      progressProcessing: "Processing OCR...",
      elapsedTimeLabel: "Elapsed Time:",
      metricTotalFiles: "Total Files",
      metricUniqueFiles: "Unique Files",
      metricDuplicates: "Duplicates Skipped",
      metricDuration: "Total Duration",
      downloadBarLabel: "Download Exported Files:",
      tabPreview: "Document Items Preview",
      tabMarkdown: "Markdown Document",
      tabFiles: "Files Table",
      copyMarkdownBtn: "Copy Markdown Text",
      copiedToClipboard: "Copied to Clipboard!",
      thFilename: "Filename",
      thParsedPage: "Parsed Page",
      thResolution: "Resolution",
      thStatus: "Status",
      statusSuccess: "Success",
      statusSkipped: "Skipped ({reason})",
      pageLabel: "Page {page}",
      pageNA: "N/A",
      emptyStateTitle: "No Documents Processed Yet",
      emptyStateDesc: "Specify an image folder or upload document files in the configuration panel on the left, then click Start Document Extraction.",
      footerText: "cOCR Workbench. Local on-device document and screenshot processing with zero external data transmission.",

      // Interactive & Error Dialogs
      apiKeyPrompt: "This server is protected by an API Key (COCR_API_KEY). Please enter your API Key:",
      specifyFolderError: "Please specify an image folder or upload document images first.",
      selectFormatError: "Select at least one output document format (Markdown, Word, or PDF).",
      startOcrError: "Failed to start OCR execution.",
      processFailedInternal: "Process stopped due to an internal error.",
      noItemsExtracted: "No document items were successfully extracted.",
      textNotDetected: "Text not detected.",
      itemNumberLabel: "Item {item} (No. {number})",
      itemLabel: "Item {item}",
      sectionHeader: "Section: {section}",
      instructionText: "({instruction})",

      // Markdown Preview Generation
      mdHeaderTitle: "# Document Extraction Results\n",
      mdExtractionTime: "Extraction Time: {time}",
      mdTotalFilesSummary: "Total Files: {total} (Unique: {unique}, Duplicates: {duplicates})",
      mdOcrDevice: "OCR Device: {device}\n",
      mdFileHeader: "## File: `{filename}`",
      mdSectionHeader: "\n### Section: {section}",
      mdItemHeading: "#### {label} (Page {page})\n",
      mdItemPromptQuestion: "**Question Text:**\n> {text}\n",
      mdItemPromptContent: "**Text Content:**\n> {text}\n",
      mdOptionsHeader: "**Answer Choices:**",
    },
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = en;
  } else if (root.cocrI18n && typeof root.cocrI18n.registerLocale === "function") {
    root.cocrI18n.registerLocale(en);
  } else {
    root.COCR_LOCALES = root.COCR_LOCALES || {};
    root.COCR_LOCALES["en"] = en;
  }
})(typeof self !== "undefined" ? self : this);
