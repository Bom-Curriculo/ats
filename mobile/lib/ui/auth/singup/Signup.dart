import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/ui/auth/login/login_page.dart';
import 'package:flutter/material.dart';

import '../../../widget/Button.dart';
import '../../../widget/InputText.dart';
import '../../../widget/Logo.dart';

class Signup extends StatefulWidget {
  const Signup({super.key});
  @override
  _Signup createState() => _Signup();
}

class _Signup extends State<Signup> {
  void doSignup() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const LoginPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Padding(
        padding: const EdgeInsets.all(45.0),
        child: Column(
          children: [
            Logo(),
            InputText(title: 'Login'),
            InputText(title: 'Retype your password', isPassword: true),
            GestureDetector(
              onTap: doSignup,
              child: Button(title: 'Signup'),
            ),
            SizedBox(height: 30.0),
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const LoginPage()),
                );
              },
              child: Text('Back to login'),
            ),
            SizedBox(height: 15.0),
          ],
        ),
      ),
    );
  }
}
