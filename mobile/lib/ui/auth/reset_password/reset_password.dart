import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:flutter/material.dart';

import '../../../widget/Button.dart';
import '../../../widget/InputText.dart';
import '../../../widget/Logo.dart';
import '../login/login_page.dart';

class ResetPassword extends StatefulWidget {
  const ResetPassword({super.key});
  @override
  _ResetPassword createState() => _ResetPassword();
}

class _ResetPassword extends State<ResetPassword> {
  void doPasswordChange() {}

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          Logo(),
          Text(
            'Type and confirm your password to change',
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          InputText(title: 'New password', isPassword: true),
          InputText(title: 'Retype your password', isPassword: true),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const LoginPage()),
              );
            },
            child: Button(title: 'Update password'),
          ),
        ],
      ),
    );
  }
}
