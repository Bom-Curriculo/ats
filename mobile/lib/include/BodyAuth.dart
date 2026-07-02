
import 'package:bomcurriculo/include/Navbar.dart';
import 'package:bomcurriculo/view/Home.dart';
import 'package:bomcurriculo/view/auth/Login.dart';
import 'package:bomcurriculo/view/auth/VerifyOTP.dart';
import 'package:bomcurriculo/view/auth/ResetPassword.dart';
import 'package:bomcurriculo/view/auth/ForgotPassword.dart';
import 'package:bomcurriculo/view/auth/Register.dart';
import 'package:flutter/material.dart';

class BodyAuth extends StatefulWidget {
  const BodyAuth({
    super.key,
    required this.child
  });

  final Widget child;

  @override
  _BodyAuth createState() => _BodyAuth();
}

class _BodyAuth extends State<BodyAuth> {

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: Colors.white,
        body: SafeArea(
        child: Stack(
          children: [

            Column(
              children: [
                Navbar(),
                Padding(
                  padding: const EdgeInsets.all(45.0),
                  child: Expanded(
                      child: SingleChildScrollView(
                          child: widget.child
                      )
                  )
                )
              ],
            ),

          ],
        ),
      )
    );
  }
}
