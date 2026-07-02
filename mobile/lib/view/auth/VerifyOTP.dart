
import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/ResetPassword.dart';
import 'package:flutter/material.dart';

import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';

class VerifyOTP extends StatefulWidget {
  const VerifyOTP({super.key});
  @override
  _VerifyOTP createState() => _VerifyOTP();
}

class _VerifyOTP extends State<VerifyOTP> {

  void doConfirmOTP() {

  }

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
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
                      builder: (context) => const ResetPassword(),
                    ),
                  );
                },
                child: Button(title: 'Confirm OTP')
              ),
            ]
        )
    );
  }
}
