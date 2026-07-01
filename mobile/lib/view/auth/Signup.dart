
import 'package:bomcurriculo/view/auth/Login.dart';
import 'package:flutter/material.dart';

import '../../include/Body.dart';
import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';

class Signup extends StatefulWidget {
  const Signup({super.key});
  @override
  _Signup createState() => _Signup();
}

class _Signup extends State<Signup> {



  @override
  Widget build(BuildContext context) {
    return Body(
        child: Padding(
          padding: const EdgeInsets.all(45.0),
          child: Column(
              children: [
                Logo(),
                InputText(title: 'Login'),
                InputText(title: 'Retype your password', isPassword: true),
                Button(title: 'Signup'),
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
                    child: Text('Efetuar login')
                ),
                SizedBox(height: 15.0),
              ]
          ),
        )
    );
  }
}
