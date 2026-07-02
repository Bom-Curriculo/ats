
import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/Home.dart';
import 'package:bomcurriculo/view/auth/Recovery.dart';
import 'package:bomcurriculo/view/auth/Signup.dart';
import 'package:bomcurriculo/widget/Button.dart';
import 'package:bomcurriculo/widget/InputText.dart';
import 'package:bomcurriculo/widget/Logo.dart';
import 'package:flutter/material.dart';

class Login extends StatefulWidget {
  const Login({super.key});
  @override
  _Login createState() => _Login();
}

class _Login extends State<Login> {

  void doLogin() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const Home(),
      ),
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
            InputText(title: 'Password', isPassword: true),
            GestureDetector(
              onTap: doLogin,
              child: Button(title: 'Login')
            ),
            SizedBox(height: 30.0),
            GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const Signup(),
                    ),
                  );
                },
                child: Text('Signup for free')
            ),
            SizedBox(height: 15.0),
            GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const Recovery(),
                    ),
                  );
                },
                child: Text('Forgot password?')
            ),
            SizedBox(height: 15.0),
          ]
                    )
      )
    );
  }
}
