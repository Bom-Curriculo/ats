import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";

export interface ReviewItem {
  id: string;
  title: string;
  description?: string;
}

export interface ReviewSection {
  id: string;
  title: string;
  items: ReviewItem[];
}

interface ResumeReviewStageProps {
  sections: ReviewSection[];
  onGenerate: (selectedItemIds: string[]) => void;
}

export function ResumeReviewStage({ sections, onGenerate }: ResumeReviewStageProps) {
  const allItemIds = sections.flatMap((section) => section.items.map((item) => item.id));
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set(allItemIds));

  function toggleItem(id: string) {
    setCheckedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  return (
    <div className="flex flex-1 items-center justify-center">
      <div className="w-full max-w-2xl">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-brand-secondary md:text-3xl dark:text-foreground">
            Confirme seus dados
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Desmarque as informações que você não quer incluir no seu currículo.
          </p>
        </div>

        <div className="mt-8 space-y-6">
          {sections.map((section) => (
            <div key={section.id}>
              <h2 className="text-sm font-semibold text-brand-secondary">{section.title}</h2>
              <ul className="mt-2 space-y-2">
                {section.items.map((item) => (
                  <li key={item.id}>
                    <label className="flex cursor-pointer items-center gap-3 rounded-lg border border-border bg-muted/50 p-3 transition-colors hover:bg-muted">
                      <Checkbox
                        checked={checkedIds.has(item.id)}
                        onCheckedChange={() => toggleItem(item.id)}
                      />
                      <div>
                        <p className="text-sm font-medium text-foreground">{item.title}</p>
                        {item.description && (
                          <p className="text-xs text-muted-foreground">{item.description}</p>
                        )}
                      </div>
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <Button className="mt-6 w-full" size="lg" onClick={() => onGenerate(Array.from(checkedIds))}>
          Gerar currículo
        </Button>
      </div>
    </div>
  );
}
