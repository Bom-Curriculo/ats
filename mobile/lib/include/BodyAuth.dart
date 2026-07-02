
import 'package:bomcurriculo/include/Navbar.dart';
import 'package:bomcurriculo/view/Home.dart';
import 'package:bomcurriculo/view/auth/Login.dart';
import 'package:bomcurriculo/view/auth/OTP.dart';
import 'package:bomcurriculo/view/auth/Password.dart';
import 'package:bomcurriculo/view/auth/Recovery.dart';
import 'package:bomcurriculo/view/auth/Signup.dart';
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
                widget.child
              ],
            ),

          ],
        ),
      )
    );
  }
}
