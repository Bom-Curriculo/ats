import 'package:bomcurriculo/view/Home.dart';
import 'package:bomcurriculo/view/SendData.dart';
import 'package:bomcurriculo/view/auth/Login.dart';
import 'package:bomcurriculo/view/auth/ResetPassword.dart';
import 'package:bomcurriculo/view/auth/ForgotPassword.dart';
import 'package:bomcurriculo/view/auth/Register.dart';
import 'package:bomcurriculo/view/auth/VerifyOTP.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Bom Currículo',
      theme: ThemeData(
        colorScheme: .fromSeed(seedColor: Colors.deepPurple),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const Home(),
        '/auth/login': (context) => const Login(),
        '/auth/register': (context) => const Register(),
        '/auth/forgot-password': (context) => const ForgotPassword(),
        '/auth/verify-otp': (context) => const VerifyOTP(),
        '/auth/reset-password': (context) => const ResetPassword(),
        '/send-data': (context) => const SendData()
      }
    );
  }
}


