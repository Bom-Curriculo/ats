import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Checkbox } from "@/components/ui/checkbox";

describe("Checkbox", () => {
  it("renders unchecked by default", () => {
    render(<Checkbox aria-label="aceitar termos" />);
    expect(screen.getByRole("checkbox")).not.toBeChecked();
  });

  it("renders checked when checked prop is true", () => {
    render(<Checkbox aria-label="aceitar termos" checked onCheckedChange={() => {}} />);
    expect(screen.getByRole("checkbox")).toBeChecked();
  });

  it("calls onCheckedChange when clicked", async () => {
    const user = userEvent.setup();
    const onCheckedChange = vi.fn();
    render(<Checkbox aria-label="aceitar termos" onCheckedChange={onCheckedChange} />);

    await user.click(screen.getByRole("checkbox"));

    expect(onCheckedChange).toHaveBeenCalledWith(true);
  });

  it("does not respond to clicks when disabled", async () => {
    const user = userEvent.setup();
    const onCheckedChange = vi.fn();
    render(<Checkbox aria-label="aceitar termos" disabled onCheckedChange={onCheckedChange} />);

    await user.click(screen.getByRole("checkbox"));

    expect(onCheckedChange).not.toHaveBeenCalled();
  });
});
