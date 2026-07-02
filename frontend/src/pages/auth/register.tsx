import { RegisterApi } from "@/api/auth/register-api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  RegisterSchema,
  type RegisterFormData,
} from "@/schemas/auth/register-schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { CircleCheck, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function Register() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    handleSubmit,
    register,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(RegisterSchema),
  });

  const mutation = useMutation({
    mutationFn: RegisterApi,

    onSuccess: () => {
      toast.success("Usuario criado com sucesso!");
      navigate("/");
    },

    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  function handleSingUp(data: RegisterFormData) {
    mutation.mutate(data);
  }

  return (
    <section className="flex min-h-screen items-center justify-center bg-white p-6">
      <div className="grid w-full max-w-7xl grid-cols-1 items-center gap-16 lg:grid-cols-2">
        <div className="flex flex-col">
          <div className="mb-10 flex items-center gap-3">
            <img
              src="/logo-dark.png"
              alt="BomCurriculo"
              className="h-14 w-auto"
            />
            <h1 className="text-3xl font-bold text-[#03206E]">
              Bom<span className="text-blue-600">Currículo</span>
            </h1>
          </div>

          <h2 className="text-5xl font-extrabold leading-[1.1] tracking-tight text-[#03206E]">
            Impulsione sua carreira
            <br />
            com <span className="text-blue-600">Inteligência Artificial.</span>
          </h2>

          <p className="mt-6 max-w-md text-lg leading-relaxed text-slate-500">
            Otimize seu currículo para sistemas ATS e destaque-se entre os
            candidatos. Soluções focadas no mercado de trabalho atual.
          </p>

          <div className="mt-10 flex flex-col gap-6">
            <div className="flex items-start gap-3">
              <CircleCheck className="mt-0.5 h-6 w-6 shrink-0 text-blue-600" />
              <div>
                <h3 className="text-base font-semibold text-[#03206E]">
                  Análise de Compatibilidade ATS
                </h3>
                <p className="text-sm text-slate-500">
                  Garanta que seu currículo seja lido corretamente pelos
                  softwares de recrutamento.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CircleCheck className="mt-0.5 h-6 w-6 shrink-0 text-blue-600" />
              <div>
                <h3 className="text-base font-semibold text-[#03206E]">
                  Otimização de Keywords
                </h3>
                <p className="text-sm text-slate-500">
                  Sugestões baseadas em inteligência de dados para sua área de
                  atuação.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="w-full rounded-2xl border border-slate-200 bg-white p-10 shadow-sm lg:p-12">
          <h2 className="mb-2 text-3xl font-bold text-[#03206E]">
            Criar sua conta
          </h2>

          <p className="mb-8 text-slate-500">
            Comece agora sua jornada profissional. Já possui conta?{" "}
            <Link
              to="/login"
              className="font-medium text-blue-600 hover:underline"
            >
              Entrar
            </Link>
          </p>

          <form onSubmit={handleSubmit(handleSingUp)} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Nome Completo
              </label>

              <Input
                className="h-14 rounded-none border-slate-200 bg-slate-50 focus-visible:ring-blue-600"
                placeholder="Ex: João Silva"
                {...register("name")}
              />

              {errors.name && (
                <p className="mt-1 text-sm text-red-500">
                  {errors.name.message}
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                E-mail Profissional
              </label>

              <Input
                className="h-14 rounded-none border-slate-200 bg-slate-50 focus-visible:ring-blue-600"
                placeholder="seu@email.com"
                {...register("email")}
              />

              {errors.email && (
                <p className="mt-1 text-sm text-red-500">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Senha
              </label>

              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  className="h-14 rounded-none border-slate-200 bg-slate-50 pr-12 focus-visible:ring-blue-600"
                  placeholder="Mínimo 8 caracteres"
                  {...register("password")}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>

              {errors.password && (
                <p className="mt-1 text-sm text-red-500">
                  {errors.password.message}
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Confirmar Senha
              </label>

              <div className="relative">
                <Input
                  type={showConfirmPassword ? "text" : "password"}
                  className="h-14 rounded-none border-slate-200 bg-slate-50 pr-12 focus-visible:ring-blue-600"
                  placeholder="Repita sua senha"
                  {...register("password_confirm")}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((v) => !v)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 rounded-none"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>

              {errors.password_confirm && (
                <p className="mt-1 text-sm text-red-500">
                  {errors.password_confirm.message}
                </p>
              )}
            </div>

            <div className="flex items-start gap-2 pt-1">
              <input
                type="checkbox"
                id="terms"
                className="mt-1 h-4 w-4 rounded-none border-slate-300 text-blue-600 focus:ring-blue-600"
              />
              <label htmlFor="terms" className="text-sm text-slate-600">
                Li e aceito os{" "}
                <a href="/termo" className="text-blue-600 hover:underline">
                  Termos de Uso
                </a>{" "}
                e{" "}
                <a href="/termos" className="text-blue-600 hover:underline">
                  Privacidade
                </a>
                .
              </label>
            </div>

            <Button
              type="submit"
              disabled={mutation.isPending}
              className="h-14 w-full rounded-none bg-[#03206E] text-lg font-semibold hover:bg-[#03206E]/90 text-white"
            >
              {mutation.isPending ? "Entrando..." : "Finalizar Cadastro"}
            </Button>
          </form>

          <p className="mt-8 border-t border-slate-100 pt-6 text-center text-xs text-slate-400">
            Protegemos seus dados de acordo com a LGPD.
          </p>
        </div>
      </div>
    </section>
  );
}
