<x-mail::message>
# Recuperação de senha

Olá, **{{ $user->name }}**.

Você solicitou a recuperação de senha em nosso sistema.

Seu código é:

# {{ $otp }}

Este código expira em **15 minutos**.

Se você não solicitou a recuperação de senha, basta ignorar este e-mail.

</x-mail::message>