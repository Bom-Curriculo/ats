import 'package:bomcurriculo/domain/dto/login_dto.dart';
import 'package:signal_form/signal_form.dart';

typedef LoginFormSchema = ({Field<String> email, Field<String> password});

LoginFormSchema loginFormSchema() => (
  email: Field<String>('email')
      .required(message: 'O e-mail é obrigatório')
      .email(message: 'E-mail inválido'),
  password: Field<String>('password')
      .required(message: 'A senha é obrigatória')
      .minLength(6, message: 'A senha deve ter pelo menos 6 caracteres'),
);

extension ParseFormExtension on FormController<LoginFormSchema> {
  LoginDto toDto() {
    return LoginDto(
      email: fields.email.value!,
      password: fields.password.value!,
    );
  }
}
