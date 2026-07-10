import { useState } from "react";

const DEFAULT_ACCEPTED_EXTENSIONS = [".pdf", ".doc", ".docx"];
const DEFAULT_MAX_SIZE_MB = 5; // até 5MB

interface UseResumeFileOptions {
  acceptedExtensions?: string[];
  maxSizeMB?: number;
}

export function useResumeFile(options?: UseResumeFileOptions) {
  const acceptedExtensions = options?.acceptedExtensions ?? DEFAULT_ACCEPTED_EXTENSIONS;
  const maxSizeMB = options?.maxSizeMB ?? DEFAULT_MAX_SIZE_MB;

  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  function selectFile(candidate: File) {
    const extension = candidate.name.slice(candidate.name.lastIndexOf(".")).toLowerCase();
    if (!acceptedExtensions.includes(extension)) {
      setError("Formato não suportado. Envie um arquivo PDF, DOC ou DOCX.");
      return;
    }
    if (candidate.size > maxSizeMB * 1024 * 1024) {
      setError(`O arquivo deve ter até ${maxSizeMB}MB.`);
      return;
    }
    setError(null);
    setFile(candidate);
  }

  function removeFile() {
    setFile(null);
    setError(null);
  }

  return { file, error, acceptedExtensions, maxSizeMB, selectFile, removeFile };
}
