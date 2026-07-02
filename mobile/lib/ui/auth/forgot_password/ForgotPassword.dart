import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/ui/auth/otp/verify_otp.dart';
import 'package:flutter/material.dart';

import '../../../widget/Button.dart';
import '../../../widget/InputText.dart';
import '../../../widget/Logo.dart';

class ForgotPassword extends StatefulWidget {
  const ForgotPassword({super.key});
  @override
  _ForgotPassword createState() => _ForgotPassword();
}

class _ForgotPassword extends State<ForgotPassword> {
  void doSendEmail() {}

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          Logo(),
          Text(
            'Forgot your password? Type your email to receive OTP code to change your password',
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          InputText(title: 'Email'),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const VerifyOTP()),
              );
            },
            child: Button(title: 'Recover password'),
          ),
        ],
      ),
    );
  }
}
