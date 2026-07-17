import {
  forgotPasswordSchema,
  type ForgotPasswordFormData,
} from "@/schemas/auth/forgot-password-schema";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { ForgotPasswordApi } from "@/api/auth/forgot-password-api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { ArrowLeft, KeyRound, Mail } from "lucide-react";

export function ForgotPassword() {
  const {
    handleSubmit,
    register,
    formState: { errors, isSubmitSuccessful },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const mutation = useMutation({
    mutationFn: ForgotPasswordApi,

    onSuccess: () => {
      toast.success("Enviamos um link de recuperação para o seu e-mail!");
    },

    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  function handleForgotPassword(data: ForgotPasswordFormData) {
    mutation.mutate(data);
  }

  const sent = isSubmitSuccessful && mutation.isSuccess;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <section className="flex flex-1 items-center justify-center bg-background p-4">
        <div className="w-full max-w-[440px] rounded-xl border border-border bg-card p-8 shadow-2xl sm:p-10">
          <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-brand-secondary/10">
            <KeyRound className="h-8 w-8 text-brand-secondary" />
          </div>

          <h1 className="mb-2 text-2xl font-bold text-foreground lg:text-3xl">
            Esqueci minha senha
          </h1>

          <p className="mb-8 text-sm text-muted-foreground lg:text-base">
            Digite seu e-mail cadastrado e enviaremos um link para você
            redefinir sua senha.
          </p>

          {sent ? (
            <div className="space-y-6">
              <p className="rounded-lg bg-brand-secondary/10 p-4 text-sm text-foreground">
                Verifique sua caixa de entrada. Se o e-mail informado estiver
                cadastrado, você receberá as instruções de recuperação em
                instantes.
              </p>

              <Link
                to="/login"
                className="flex items-center justify-center gap-2 text-sm font-medium text-brand-secondary hover:underline"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar para o login
              </Link>
            </div>
          ) : (
            <form
              onSubmit={handleSubmit(handleForgotPassword)}
              className="space-y-6"
            >
              <div>
                <label className="mb-2 block font-medium text-foreground">
                  Endereço de e-mail
                </label>

                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />

                  <Input
                    type="email"
                    className="h-12 rounded-lg border-input-border-strong pl-10 text-foreground lg:h-14"
                    placeholder="seu@email.com.br"
                    {...register("email")}
                  />
                </div>

                {errors.email && (
                  <p className="mt-1 text-sm text-destructive">
                    {errors.email.message}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={mutation.isPending}
                className="h-12 w-full gap-2 rounded-lg bg-brand-secondary text-base text-white hover:bg-brand-secondary/90 lg:h-14 lg:text-lg"
              >
                {mutation.isPending
                  ? "Enviando..."
                  : "Enviar link de recuperação"}
              </Button>

              <Link
                to="/login"
                className="flex items-center justify-center gap-2 text-sm font-medium text-brand-secondary hover:underline"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar para o login
              </Link>
            </form>
          )}
        </div>
      </section>

      <Footer />
    </div>
  );
}
