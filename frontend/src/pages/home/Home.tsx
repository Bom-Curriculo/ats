"use client";

import { Bell } from "lucide-react";

import { ModeToggle } from "@/components/mode-toggle";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <>
      <body></body>
      <header className="bg-gray-50 px-8 py-4 dark:bg-[#03206E] border-b border-solid border-gray-300 dark:border-blue-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-2">
            <img
              src="/logo-dark.png"
              alt="BomCurriculo"
              className="h-10 w-auto dark:hidden"
            />

            <img
              src="/logo.png"
              alt="BomCurriculo"
              className="hidden h-10 w-auto dark:block"
            />

            <h1 className="text-2xl font-bold">
              Bom
              <span className="text-blue-600">Curriculo</span>
            </h1>
          </div>

          <nav>
            <ul className="flex items-center gap-8 text-lg font-medium">
              <li className="cursor-pointer hover:text-blue-600">Dashboard</li>
              <li className="cursor-pointer hover:text-blue-600">Editor</li>
              <li className="cursor-pointer hover:text-blue-600">Vagas</li>
              <li className="cursor-pointer hover:text-blue-600">Preços</li>
            </ul>
          </nav>

          <div className="flex items-center gap-4">
            <Button className="rounded-2xl border border-blue-600 bg-transparent px-6 py-2 text-blue-600 hover:bg-blue-600 hover:text-white">
              <a href="/login">Entrar</a>
            </Button>

            <Bell
              size={24}
              className="cursor-pointer text-gray-700 hover:text-blue-600 dark:text-gray-300"
            />

            <ModeToggle />
          </div>
        </div>
      </header>

      <footer>...</footer>
    </>
  );
}
