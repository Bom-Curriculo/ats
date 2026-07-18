import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ResumeReviewStage, type ReviewSection } from "@/components/resume-upload/ResumeReviewStage";

const sections: ReviewSection[] = [
  {
    id: "experiences",
    title: "Experiências",
    items: [
      { id: "exp-1", title: "Bom Currículo", description: "De: 02/06/2025 à 02/07/2026" },
      { id: "exp-2", title: "WhiteHats", description: "De: 02/06/2025 à 02/07/2026" },
    ],
  },
  {
    id: "skills",
    title: "Habilidades",
    items: [{ id: "skill-php", title: "PHP", description: "15 anos de experiência" }],
  },
];

describe("ResumeReviewStage", () => {
  it("renders all sections and items with checkboxes checked by default", () => {
    render(<ResumeReviewStage sections={sections} onGenerate={vi.fn()} />);

    expect(screen.getByText("Experiências")).toBeInTheDocument();
    expect(screen.getByText("Habilidades")).toBeInTheDocument();
    expect(screen.getByText("Bom Currículo")).toBeInTheDocument();
    expect(screen.getByText("PHP")).toBeInTheDocument();

    for (const checkbox of screen.getAllByRole("checkbox")) {
      expect(checkbox).toBeChecked();
    }
  });

  it("calls onGenerate with every item id when nothing is unchecked", async () => {
    const user = userEvent.setup();
    const onGenerate = vi.fn();
    render(<ResumeReviewStage sections={sections} onGenerate={onGenerate} />);

    await user.click(screen.getByRole("button", { name: /gerar currículo/i }));

    expect(onGenerate).toHaveBeenCalledTimes(1);
    expect(onGenerate.mock.calls[0][0]).toEqual(
      expect.arrayContaining(["exp-1", "exp-2", "skill-php"])
    );
    expect(onGenerate.mock.calls[0][0]).toHaveLength(3);
  });

  it("excludes an item from onGenerate after it's unchecked", async () => {
    const user = userEvent.setup();
    const onGenerate = vi.fn();
    render(<ResumeReviewStage sections={sections} onGenerate={onGenerate} />);

    const phpCheckbox = screen.getAllByRole("checkbox")[2];
    await user.click(phpCheckbox);
    await user.click(screen.getByRole("button", { name: /gerar currículo/i }));

    const selectedIds = onGenerate.mock.calls[0][0] as string[];
    expect(selectedIds).not.toContain("skill-php");
    expect(selectedIds).toHaveLength(2);
  });
});
