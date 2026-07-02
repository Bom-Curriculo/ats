import 'package:bomcurriculo/ui/Home.dart';
import 'package:bomcurriculo/ui/auth/login/login_page.dart';
import 'package:bomcurriculo/ui/auth/register/register.dart';
import 'package:bomcurriculo/ui/auth/forgot_password/ForgotPassword.dart';
import 'package:bomcurriculo/ui/auth/otp/verify_otp.dart';
import 'package:bomcurriculo/ui/auth/reset_password/reset_password.dart';
import 'package:bomcurriculo/ui/resume/MyResumes.dart';
import 'package:bomcurriculo/ui/resume/ValidateResume.dart';
import 'package:bomcurriculo/ui/resume/GenerateResume.dart';
import 'package:go_router/go_router.dart';

final router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (context, state) => Home()),
    GoRoute(path: '/auth/login', builder: (context, state) => LoginPage()),
    GoRoute(path: '/auth/register', builder: (context, state) => Register()),
    GoRoute(
      path: '/auth/forgot-password',
      builder: (context, state) => ForgotPassword(),
    ),
    GoRoute(path: '/auth/verify-otp', builder: (context, state) => VerifyOTP()),
    GoRoute(
      path: '/auth/reset-password',
      builder: (context, state) => ResetPassword(),
    ),
    GoRoute(
      path: '/validate-resume',
      builder: (context, state) => ValidateResume(),
    ),
    GoRoute(path: '/my-resumes', builder: (context, state) => MyResumes()),
    GoRoute(
      path: '/generate-resume',
      builder: (context, state) => GenerateResume(),
    ),
  ],
);
