import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/view/auth/ViewForgotPassword.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:bomcurriculo/view/auth/ViewRegister.dart';
import 'package:bomcurriculo/view/auth/ViewResetPassword.dart';
import 'package:bomcurriculo/view/auth/ViewVerifyOTP.dart';
import 'package:bomcurriculo/view/resume/ViewMyResumes.dart';
import 'package:bomcurriculo/view/resume/ViewValidateResume.dart';
import 'package:bomcurriculo/view/resume/ViewGenerateResume.dart';
import 'package:go_router/go_router.dart';

final router = GoRouter(
  routes: [
    GoRoute(
        path: '/',
        builder: (context, state) => ViewHome()
    ),
    GoRoute(
        path: '/auth/login',
        builder: (context, state) => ViewLogin()
    ),
    GoRoute(
        path: '/auth/register',
        builder: (context, state) => ViewRegister()
    ),
    GoRoute(
      path: '/auth/forgot-password',
      builder: (context, state) => ViewForgotPassword(),
    ),
    GoRoute(
        path: '/auth/verify-otp',
        builder: (context, state) => ViewVerifyOTP()
    ),
    GoRoute(
      path: '/auth/reset-password',
      builder: (context, state) => ViewResetPassword(),
    ),
    GoRoute(
      path: '/validate-resume',
      builder: (context, state) => ViewValidateResume(),
    ),
    GoRoute(
        path: '/my-resumes',
        builder: (context, state) => ViewMyResumes()
    ),
    GoRoute(
      path: '/generate-resume',
      builder: (context, state) => ViewGenerateResume(),
    ),
  ],
);
