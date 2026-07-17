import { TriangleAlert } from "lucide-react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DeleteResumeDialogProps {
  open: boolean;
  fileName?: string;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}

export default function DeleteResumeDialog({
  open,
  fileName,
  onOpenChange,
  onConfirm,
}: DeleteResumeDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <div
            aria-hidden="true"
            className="flex size-11 shrink-0 items-center justify-center rounded-full bg-destructive/10"
          >
            <TriangleAlert className="size-5 text-destructive" />
          </div>
          <AlertDialogTitle>Excluir currículo</AlertDialogTitle>
          <AlertDialogDescription>
            Tem certeza que deseja excluir{" "}
            {fileName ? <span className="font-medium text-foreground">{fileName}</span> : "este currículo"}? Essa
            ação não poderá ser desfeita.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className={cn(buttonVariants({ variant: "destructive" }), "bg-destructive text-white hover:bg-destructive/90")}
          >
            Excluir currículo
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
