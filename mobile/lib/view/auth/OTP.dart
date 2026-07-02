
import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/Password.dart';
import 'package:flutter/material.dart';

import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';

class OTP extends StatefulWidget {
  const OTP({super.key});
  @override
  _OTP createState() => _OTP();
}

class _OTP extends State<OTP> {

  void doConfirmOTP() {

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
                    'Type the OTP sent to your email to change your password',
                    textAlign: TextAlign.center
                ),
                SizedBox(height: 30.0),
                InputText(title: 'OTP'),
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const Password(),
                      ),
                    );
                  },
                  child: Button(title: 'Confirm OTP')
                ),
              ]
          ),
        )
    );
  }
}
