
import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/Login.dart';
import 'package:flutter/material.dart';

import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';

class Register extends StatefulWidget {
  const Register({super.key});
  @override
  _Register createState() => _Register();
}

class _Register extends State<Register> {

  void doSignup() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const Login(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
        child: Column(
            children: [
              Logo(),
              Text(
                  'Signup for free',
                  textAlign: TextAlign.center
              ),
              SizedBox(height: 30.0),
              InputText(title: 'Login'),
              InputText(title: 'Password', isPassword: true),
              InputText(title: 'Confirm your password', isPassword: true),
              GestureDetector(
                  onTap: doSignup,
                  child: Button(title: 'Signup')
              ),
              SizedBox(height: 30.0),
              GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const Login(),
                      ),
                    );
                  },
                  child: Text('Back to login')
              ),
              SizedBox(height: 15.0),
            ]
        )
    );
  }
}
