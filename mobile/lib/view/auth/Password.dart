
import 'package:flutter/material.dart';

import '../../include/Body.dart';
import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';
import 'Login.dart';

class Password extends StatefulWidget {
  const Password({super.key});
  @override
  _Password createState() => _Password();
}

class _Password extends State<Password> {



  @override
  Widget build(BuildContext context) {
    return Body(
        child: Padding(
          padding: const EdgeInsets.all(45.0),
          child: Column(
              children: [
                Logo(),
                InputText(title: 'New password', isPassword: true),
                InputText(title: 'Retype your password', isPassword: true),
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const Login(),
                      ),
                    );
                  },
                  child: Button(title: 'Update password')
                ),
              ]
          ),
        )
    );
  }
}
