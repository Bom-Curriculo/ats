import 'package:bomcurriculo/routes.dart';
import 'package:bomcurriculo/ui/Home.dart';
import 'package:bomcurriculo/ui/resume/ValidateResume.dart';
import 'package:bomcurriculo/ui/auth/login/login_page.dart';
import 'package:bomcurriculo/ui/auth/reset_password/reset_password.dart';
import 'package:bomcurriculo/ui/auth/forgot_password/ForgotPassword.dart';
import 'package:bomcurriculo/ui/auth/register/register.dart';
import 'package:bomcurriculo/ui/auth/otp/verify_otp.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: router,
      debugShowCheckedModeBanner: false,
      title: 'Bom Currículo',
      theme: ThemeData(colorScheme: .fromSeed(seedColor: Colors.deepPurple)),
    );
  }
}
