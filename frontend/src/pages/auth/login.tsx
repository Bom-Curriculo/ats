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
      navigate("/");
    },

    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  function handleSignIn(data: LoginFormData) {
    mutation.mutate(data);
  }
  return (
    <section className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <div className="flex w-full min-h-200 max-w-7xl overflow-hidden  bg-white shadow-2xl">
        <div className="flex w-1/2 flex-col bg-[#03206E] p-12 text-white">
          <div className="mb-10 flex items-center gap-4">
            <div className="h-20 w-0.5 bg-white/60" />

            <img
              src="/logo.png"
              alt="BomCurriculo"
              className="h-45 w-auto"
            />

            <div>
              <h1 className="text-5xl font-bold">
                Bom
                <span className="text-blue-400">Currículo</span>
              </h1>

              <p className="mt-2 text-xl text-white/80">
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
            <div className="flex-1 rounded-none border border-white/10 bg-white/5 p-6 ">
              <h2 className="text-4xl font-bold">1k+</h2>
              <p className="text-white/70">APROVAÇÕES ATS</p>
            </div>

            <div className="flex-1 rounded-none border border-white/10 bg-white/5 p-6">
              <h2 className="text-4xl font-bold">98%</h2>
              <p className="text-white/70">TAXA DE SUCESSO</p>
            </div>
          </div>
        </div>

        <div className="flex w-1/2 items-center justify-center bg-white p-16">
          <div className="w-full max-w-md">
            <h2 className="mb-2 text-4xl font-bold text-[#03206E]">
              Acesse sua conta
            </h2>

            <p className="mb-10 text-slate-500">
              Insira suas credenciais corporativas.
            </p>

            <form onSubmit={handleSubmit(handleSignIn)} className="space-y-6">
              <div>

                <label className="mb-2 block font-medium text-[#03206E] ">

                  Endereço de e-mail
                </label>

                <Input

                  className="h-14 rounded-none border-[#03206E]"

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

                <label className="mb-2 block font-medium text-[#03206E]">
                  Senha
                </label>

                <Input
                  type="password"
                  className="h-14 rounded-none border-[#03206E]"
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

                className="h-14 w-full bg-[#03206E] text-white text-lg rounded-none"

              >
                {mutation.isPending ? "Entrando..." : "Acessar Plataforma"}
              </Button>

              <p className="pt-6 text-center text-slate-600">
                Novo usuário?{" "}
                <Link to="/register" className="text-blue-600 hover:underline">
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
