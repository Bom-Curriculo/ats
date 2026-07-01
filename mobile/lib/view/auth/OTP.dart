
import 'package:bomcurriculo/view/auth/Password.dart';
import 'package:flutter/material.dart';

import '../../include/Body.dart';
import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';
import 'Login.dart';

class OTP extends StatefulWidget {
  const OTP({super.key});
  @override
  _OTP createState() => _OTP();
}

class _OTP extends State<OTP> {



  @override
  Widget build(BuildContext context) {
    return Body(
        child: Padding(
          padding: const EdgeInsets.all(45.0),
          child: Column(
              children: [
                Logo(),
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
