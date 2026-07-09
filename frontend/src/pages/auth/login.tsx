import { loginSchema, type LoginFormData } from "@/schemas/auth/login-schema";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { LoginApi } from "@/api/auth/login-api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function Login() {
  const navigate = useNavigate();

  const {
    handleSubmit,
    register,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });
  const mutation = useMutation({
    mutationFn: LoginApi,

    onSuccess: () => {
      toast.success("Usuario autenticado com sucesso!");
      navigate("/dashboard");
    },

    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  function handleSignIn(data: LoginFormData) {
    mutation.mutate(data);
  }
  return (
    <section className="flex min-h-screen items-center justify-center bg-slate-100 p-4 md:p-6">
      <div className="flex w-full max-w-7xl flex-col overflow-hidden bg-white shadow-2xl lg:flex-row">
        <div className="hidden w-full flex-col bg-brand-secondary p-8 text-white lg:flex lg:w-1/2 lg:p-12">
          <div className="mb-10 flex items-center gap-4">
            <div className="h-20 w-0.5 bg-white/60" />

            <img
              src="/logo.png"
              alt="BomCurriculo"
              className="h-24 w-auto lg:h-32"
            />

            <div>
              <h1 className="text-3xl font-bold lg:text-5xl">
                Bom
                <span className="text-brand-primary">Currículo</span>
              </h1>

              <p className="mt-2 text-sm text-white/80 lg:text-xl">
                ATS INTELIGENTE. RESULTADOS REAIS.
              </p>
            </div>
          </div>

          <div className="mb-8 overflow-hidden rounded-lg">
            <img
              src="/image-background-login.png"
              alt="Preview"
              className="w-full object-cover"
            />
          </div>

          <div className="flex gap-4">
            <div className="flex-1 border border-white/10 bg-white/5 p-4 lg:p-6">
              <h2 className="text-2xl font-bold lg:text-4xl">1k+</h2>
              <p className="text-sm text-white/70 lg:text-base">
                APROVAÇÕES ATS
              </p>
            </div>

            <div className="flex-1 border border-white/10 bg-white/5 p-4 lg:p-6">
              <h2 className="text-2xl font-bold lg:text-4xl">98%</h2>
              <p className="text-sm text-white/70 lg:text-base">
                TAXA DE SUCESSO
              </p>
            </div>
          </div>
        </div>

        <div className="flex w-full items-center justify-center bg-white p-6 sm:p-8 md:p-12 lg:w-1/2 lg:p-16">
          <div className="w-full max-w-md">
            <h2 className="mb-2 text-3xl font-bold text-slate-900 lg:text-4xl">
              Acesse sua conta
            </h2>

            <p className="mb-8 text-sm text-slate-500 lg:mb-10 lg:text-base">
              Insira suas credenciais corporativas.
            </p>

            <form
              onSubmit={handleSubmit(handleSignIn)}
              className="space-y-5 lg:space-y-6"
            >
              <div>
                <label className="mb-2 block font-medium text-slate-900">
                  Endereço de e-mail
                </label>

                <Input
                  className="h-12 rounded-none border-slate-900 text-slate-900 lg:h-14"
                  placeholder="nome@exemplo.com.br"
                  {...register("email")}
                />

                {errors.email && (
                  <p className="mt-1 text-sm text-red-500">
                    {errors.email.message}
                  </p>
                )}
              </div>

              <div>
                <label className="mb-2 block font-medium text-slate-900">
                  Senha
                </label>

                <Input
                  type="password"
                  className="h-12 rounded-none border-slate-900 text-slate-900 lg:h-14"
                  placeholder="••••••••"
                  {...register("password")}
                />

                {errors.password && (
                  <p className="mt-1 text-sm text-red-500">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={mutation.isPending}
                className="h-12 w-full rounded-none bg-brand-secondary text-base text-white hover:bg-brand-secondary/80 lg:h-14 lg:text-lg"
              >
                {mutation.isPending ? "Entrando..." : "Acessar Plataforma"}
              </Button>

              <p className="pt-4 text-center text-sm text-slate-600 lg:pt-6">
                Novo usuário?{" "}
                <Link to="/register" className="text-slate-900 hover:underline">
                  Criar conta profissional
                </Link>
              </p>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
