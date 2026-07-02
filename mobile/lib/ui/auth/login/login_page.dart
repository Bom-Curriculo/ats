import 'package:bomcurriculo/ui/auth/login/login_form.dart';
import 'package:bomcurriculo/ui/auth/login/login_viewmodel.dart';
import 'package:flutter/material.dart';
import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/ui/Home.dart';
import 'package:bomcurriculo/widget/Logo.dart';
import 'package:go_router/go_router.dart';
import 'package:signal_form/signal_form.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override
  _Login createState() => _Login();
}

class _Login extends State<LoginPage> {
  final viewModel = LoginViewModel();
  late final form = formCtrl(() => loginFormSchema());

  @override
  void dispose() {
    form.dispose();
    super.dispose();
  }

  void _goHome(BuildContext context) {
    context.go('/home');
  }

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          Logo(),
          SignalTextField(
            field: form.fields.email,
            decoration: InputDecoration(labelText: 'Email'),
          ),
          SignalTextField(
            field: form.fields.password,
            decoration: InputDecoration(labelText: 'Password'),
          ),
          ListenableBuilder(
            listenable: form,
            builder: (context, _) {
              return ElevatedButton(
                onPressed: form.valid && !form.isSubmitting
                    ? () => form.submit((form) async {
                        viewModel.login(form.toDto());
                      })
                    : null,
                child: form.isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Login'),
              );
            },
          ),
          SizedBox(height: 30.0),
          GestureDetector(
            onTap: () => context.go('/auth/register'),
            child: Text('Signup for free'),
          ),
          SizedBox(height: 15.0),
          GestureDetector(
            onTap: () => context.go('/auth/forgot-password'),
            child: Text('Forgot password?'),
          ),
          SizedBox(height: 15.0),
        ],
      ),
    );
  }
}
