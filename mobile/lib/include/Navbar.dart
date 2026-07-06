import 'package:bomcurriculo/service/API.dart';
import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/view/auth/ViewForgotPassword.dart';
import 'package:bomcurriculo/view/auth/ViewRegister.dart';
import 'package:bomcurriculo/view/auth/ViewResetPassword.dart';
import 'package:bomcurriculo/view/auth/ViewVerifyOTP.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:bomcurriculo/view/resume/ViewGenerateResume.dart';
import 'package:bomcurriculo/view/resume/ViewMyResumes.dart';
import 'package:bomcurriculo/view/resume/ViewValidateResume.dart';
import 'package:bomcurriculo/widget/WidgetButtonIcon.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../config.dart';
import '../service/DB.dart';

class Navbar extends StatelessWidget implements PreferredSizeWidget {
  const Navbar({super.key, this.onMenuChanged});

  final VoidCallback? onMenuChanged;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  Future<void> logout(BuildContext context) async {
    await API().get('auth/logout');
    await DB.instance.clear();
    context.go("/auth/login");
  }

  @override
  Widget build(BuildContext context) {
    var links = [
      {'title': 'Home', 'widget': const ViewHome()},
      {'title': 'My resumes', 'widget': const ViewMyResumes()},
      {'title': 'Validate resume', 'widget': const ViewValidateResume()},
      {'title': 'Generate resume', 'widget': const ViewGenerateResume()},
      {'title': 'Login', 'widget': const ViewLogin()},
      {'title': 'Register', 'widget': const ViewRegister()},
      {'title': 'Forgot password', 'widget': const ViewForgotPassword()},
      {'title': 'Verify OTP', 'widget': const ViewVerifyOTP()},
      {'title': 'Reset Password', 'widget': ViewResetPassword(otp: "123456")},
      {'title': 'Sair', 'action': () => logout(context)},
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
        child: Text(
          appTitle,
          style: TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 18.0,
            color: Colors.black,
          ),
        ),
      ),
      actions: [
        PopupMenuButton<dynamic>(
          icon: const WidgetButtonIcon(icon: Icons.menu, color: Color(0xFFDDDDDD)),
          onSelected: (item) {
            if (item is Function) {
              item();
              return;
            }
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => item as Widget),
            );
          },
          itemBuilder: (BuildContext context) {
            return links.map((link) {
              return PopupMenuItem<dynamic>(
                value: link['action'] ?? link['widget'],
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