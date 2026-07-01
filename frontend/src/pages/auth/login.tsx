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
    <>
      <section>
        <h1>TELA LOGIN.TSX</h1>
        <form onSubmit={handleSubmit(handleSignIn)} className="space-y-5">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Email
            </label>

            <Input
              className="h-12 rounded-xl border-slate-200 bg-slate-50 transition focus-visible:ring-2 "
              placeholder="empresa@email.com"
              {...register("email")}
            />

            {errors.email && (
              <p className="mt-1 text-sm text-red-500">
                {errors.email.message}
              </p>
            )}
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-medium text-slate-700">
                Senha
              </label>
            </div>

            <Input
              type="password"
              className="h-12 rounded-xl border-slate-200 bg-slate-50 transition focus-visible:ring-2 "
              placeholder="••••••••"
              {...register("password")}
            />

            {errors.password && (
              <p className="mt-1 text-sm text-red-500">
                {errors.password.message}
              </p>
            )}
          </div>

          {mutation.isError && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-500">
              {(mutation.error as Error).message}
            </div>
          )}

          <Button
            type="submit"
            disabled={mutation.isPending}
            className="h-12 w-full rounded-xl bg-linear-to-r cursor-pointer text-base font-semibold shadow-lg transition hover:opacity-90"
          >
            {mutation.isPending ? "Entrando..." : "Entrar"}
          </Button>

          <p className="text-center text-sm text-slate-600">
            Não possui conta?{" "}
            <Link to="/register" className="font-semibold  hover:underline">
              Cadastre-se
            </Link>
          </p>
        </form>
      </section>
    </>
  );
}
