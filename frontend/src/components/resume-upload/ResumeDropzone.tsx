import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";

interface ResumeDropzoneProps {
  acceptedExtensions: string[];
  maxSizeMB: number;
  onFileSelected: (file: File) => void;
}

export function ResumeDropzone({ acceptedExtensions, maxSizeMB, onFileSelected }: ResumeDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) onFileSelected(dropped);
  }

  function handleInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0];
    if (selected) onFileSelected(selected);
    event.target.value = "";
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(event) => event.key === "Enter" && inputRef.current?.click()}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`flex cursor-pointer flex-col items-center gap-3 rounded-2xl border-2 border-dashed p-10 text-center transition-colors ${
        isDragging
          ? "border-brand-primary bg-brand-primary-tint/40"
          : "border-border bg-card hover:border-brand-primary/50"
      }`}
    >
      <span className="flex size-14 items-center justify-center rounded-full bg-brand-primary-tint">
        <UploadCloud className="size-6 text-brand-primary" />
      </span>
      <div>
        <p className="font-medium">Arraste seu currículo aqui</p>
        <p className="mt-1 text-sm text-muted-foreground">
          ou clique para selecionar —{" "}
          {acceptedExtensions.map((ext) => ext.replace(".", "").toUpperCase()).join(", ")} até {maxSizeMB}MB
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={acceptedExtensions.join(",")}
        className="hidden"
        onChange={handleInputChange}
      />
    </div>
  );
}
