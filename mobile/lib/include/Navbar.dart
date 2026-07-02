import 'package:bomcurriculo/ui/Home.dart';
import 'package:bomcurriculo/ui/auth/forgot_password/ForgotPassword.dart';
import 'package:bomcurriculo/ui/auth/login/login_page.dart';
import 'package:bomcurriculo/ui/auth/register/register.dart';
import 'package:bomcurriculo/ui/auth/reset_password/reset_password.dart';
import 'package:bomcurriculo/ui/auth/otp/verify_otp.dart';
import 'package:bomcurriculo/ui/resume/GenerateResume.dart';
import 'package:bomcurriculo/ui/resume/MyResumes.dart';
import 'package:bomcurriculo/ui/resume/ValidateResume.dart';
import 'package:bomcurriculo/widget/ButtonIcon.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class Navbar extends StatelessWidget implements PreferredSizeWidget {
  const Navbar({super.key, this.onMenuChanged});

  final VoidCallback? onMenuChanged;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    var links = [
      {'title': 'Home', 'widget': const Home()},
      {'title': 'My resumes', 'widget': const MyResumes()},
      {'title': 'Validate resume', 'widget': const ValidateResume()},
      {'title': 'Generate resume', 'widget': const GenerateResume()},
      {'title': 'Login', 'widget': const LoginPage()},
      {'title': 'Register', 'widget': const Register()},
      {'title': 'Recovery', 'widget': const ForgotPassword()},
      {'title': 'OTP', 'widget': const VerifyOTP()},
      {'title': 'Password', 'widget': const ResetPassword()},
      {'title': 'Sair', 'widget': const LoginPage()},
    ];

    return AppBar(
      backgroundColor: const Color(0xFFEEEEEE),
      elevation: 0,
      automaticallyImplyLeading: false,
      titleSpacing: 11.0,
      title: GestureDetector(
        onTap: () {
          context.go("/");
        },
        child: const Text(
          'Bom Currículo',
          style: TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 18.0,
            color: Colors.black,
          ),
        ),
      ),
      actions: [
        PopupMenuButton<Widget>(
          icon: const ButtonIcon(icon: Icons.menu, color: Color(0xFFDDDDDD)),
          onSelected: (Widget widget) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => widget),
            );
          },
          itemBuilder: (BuildContext context) {
            return links.map((link) {
              return PopupMenuItem<Widget>(
                value: link['widget'] as Widget,
                child: Text(link['title'] as String),
              );
            }).toList();
          },
        ),
        const SizedBox(width: 5.0),
      ],
    );
  }
}
