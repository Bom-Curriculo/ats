
import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/VerifyOTP.dart';
import 'package:flutter/material.dart';

import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';

class Recovery extends StatefulWidget {
  const Recovery({super.key});
  @override
  _Recovery createState() => _Recovery();
}

class _Recovery extends State<Recovery> {

  void doSendEmail() {

  }

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
        child: Padding(
          padding: const EdgeInsets.all(45.0),
          child: Column(
              children: [
                Logo(),
                Text(
                    'Forgot your password? Type your email to receive OTP code to change your password',
                    textAlign: TextAlign.center
                ),
                SizedBox(height: 30.0),
                InputText(title: 'Email'),
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const VerifyOTP(),
                      ),
                    );
                  },
                  child: Button(title: 'Recover password')
                ),
              ]
          ),
        )
    );
  }
}