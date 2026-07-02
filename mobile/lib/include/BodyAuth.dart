import 'package:bomcurriculo/include/Navbar.dart';
import 'package:bomcurriculo/ui/Home.dart';
import 'package:bomcurriculo/ui/auth/login/login_page.dart';
import 'package:bomcurriculo/ui/auth/otp/verify_otp.dart';
import 'package:bomcurriculo/ui/auth/reset_password/reset_password.dart';
import 'package:bomcurriculo/ui/auth/forgot_password/ForgotPassword.dart';
import 'package:bomcurriculo/ui/auth/register/register.dart';
import 'package:flutter/material.dart';

class BodyAuth extends StatefulWidget {
  const BodyAuth({super.key, required this.child});

  final Widget child;

  @override
  _BodyAuth createState() => _BodyAuth();
}

class _BodyAuth extends State<BodyAuth> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const Navbar(),
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(45.0),
                    child: SingleChildScrollView(child: widget.child),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
