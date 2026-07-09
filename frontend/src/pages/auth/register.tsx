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
    <section className="flex min-h-screen items-center justify-center bg-slate-100 p-4 md:p-6">
      <div className="flex w-full max-w-7xl overflow-hidden bg-white shadow-2xl">
        <div className="hidden w-1/2 flex-col bg-brand-secondary p-12 text-white lg:flex">
          <div className="mb-10 flex items-center gap-4">
            <div className="h-20 w-0.5 bg-white/60" />

            <img src="/logo.png" alt="BomCurriculo" className="h-32 w-auto" />

            <div>
              <h1 className="text-5xl font-bold">
                Bom<span className="text-brand-primary">Currículo</span>
              </h1>

              <p className="mt-2 text-xl text-white/80">
                ATS INTELIGENTE. RESULTADOS REAIS.
              </p>
            </div>
          </div>

          <div className="mb-10">
            <h2 className="text-4xl font-bold leading-tight">
              Impulsione sua carreira
              <br />
              com <span className="text-brand-primary">Inteligência Artificial</span>
            </h2>

            <p className="mt-6 max-w-lg text-lg text-white/70">
              Otimize seu currículo para sistemas ATS e destaque-se entre os
              candidatos. Soluções focadas no mercado de trabalho atual.
            </p>
          </div>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <CircleCheck className="mt-1 h-6 w-6 shrink-0 text-brand-primary" />

              <div>
                <h3 className="font-semibold">
                  Análise de Compatibilidade ATS
                </h3>

                <p className="text-white/70">
                  Garanta que seu currículo seja lido corretamente pelos
                  softwares de recrutamento.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <CircleCheck className="mt-1 h-6 w-6 shrink-0 text-brand-primary" />

              <div>
                <h3 className="font-semibold">Otimização de Keywords</h3>

                <p className="text-white/70">
                  Sugestões baseadas em inteligência de dados para sua área de
                  atuação.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex w-full items-center justify-center bg-white p-6 sm:p-8 lg:w-1/2 lg:p-16">
          <div className="w-full max-w-md">
            <h2 className="mb-2 text-4xl font-bold text-slate-900">
              Criar sua conta
            </h2>

            <p className="mb-10 text-slate-500">
              Comece sua jornada profissional.{" "}
              <Link
                to="/login"
                className="font-medium text-brand-secondary hover:underline"
              >
                Já possui conta?
              </Link>
            </p>

            <form onSubmit={handleSubmit(handleSingUp)} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Nome Completo
                </label>

                <Input
                  className="h-12 rounded-none border-slate-900 bg-slate-50 text-brand-secondary focus-visible:ring-brand-primary sm:h-14"
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
                  className="h-12 rounded-none border-slate-900 bg-slate-50 text-brand-secondary focus-visible:ring-brand-primary sm:h-14"
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
                    className="h-12 rounded-none border-slate-900 bg-slate-50 pr-12 text-brand-secondary focus-visible:ring-brand-primary sm:h-14"
                    placeholder="Mínimo 8 caracteres"
                    {...register("password")}
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-brand-secondary hover:text-slate-600"
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
                    className="h-12 rounded-none border-slate-900 bg-slate-50 pr-12 text-brand-secondary focus-visible:ring-brand-primary sm:h-14"
                    placeholder="Repita sua senha"
                    {...register("password_confirm")}
                  />

                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
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

              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  id="terms"
                  className="mt-1 h-4 w-4 border-slate-300"
                />

                <label htmlFor="terms" className="text-sm text-slate-600">
                  Li e aceito os{" "}
                  <a href="/termo" className="text-brand-primary hover:underline">
                    Termos de Uso
                  </a>{" "}
                  e{" "}
                  <a href="/termos" className="text-brand-primary hover:underline">
                    Privacidade
                  </a>
                  .
                </label>
              </div>

              <Button
                type="submit"
                disabled={mutation.isPending}
                className="h-12 w-full rounded-none bg-brand-secondary text-base font-semibold text-white hover:bg-brand-secondary/90 sm:h-14 sm:text-lg"
              >
                {mutation.isPending ? "Entrando..." : "Finalizar Cadastro"}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
