
import 'package:bomcurriculo/view/auth/OTP.dart';
import 'package:bomcurriculo/view/auth/Password.dart';
import 'package:flutter/material.dart';

import '../../include/Body.dart';
import '../../widget/Button.dart';
import '../../widget/InputText.dart';
import '../../widget/Logo.dart';

class Recovery extends StatefulWidget {
  const Recovery({super.key});
  @override
  _Recovery createState() => _Recovery();
}

class _Recovery extends State<Recovery> {



  @override
  Widget build(BuildContext context) {
    return Body(
        child: Padding(
          padding: const EdgeInsets.all(45.0),
          child: Column(
              children: [
                Logo(),
                InputText(title: 'Email'),
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const OTP(),
                      ),
                    );
                  },
                  child: Button(title: 'Recover password')
                ),
              ]
          ),
        )
    );
  }
}
