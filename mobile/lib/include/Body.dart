import 'package:bomcurriculo/include/Navbar.dart';
import 'package:bomcurriculo/ui/Home.dart';
import 'package:bomcurriculo/ui/resume/MyResumes.dart';
import 'package:bomcurriculo/ui/resume/ValidateResume.dart';
import 'package:bomcurriculo/ui/auth/login/login_page.dart';
import 'package:bomcurriculo/ui/auth/otp/verify_otp.dart';
import 'package:bomcurriculo/ui/auth/reset_password/reset_password.dart';
import 'package:bomcurriculo/ui/auth/forgot_password/ForgotPassword.dart';
import 'package:bomcurriculo/ui/auth/register/register.dart';
import 'package:flutter/material.dart';

import '../ui/resume/GenerateResume.dart';

class Body extends StatefulWidget {
  const Body({super.key, required this.child});

  final Widget child;

  @override
  _Body createState() => _Body();
}

class _Body extends State<Body> {
  static const double navbarHeight = 50.0;
  bool boolMenu = false;

  @override
  Widget build(BuildContext context) {
    // Por hora as rotas existentes
    // TODO: trocar por links reais no futuro

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: Navbar(
        onMenuChanged: () {
          setState(() {
            boolMenu = !boolMenu;
          });
        },
      ),
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                Expanded(child: SingleChildScrollView(child: widget.child)),
              ],
            ),

            // Menu
          ],
        ),
      ),
    );
  }
}
