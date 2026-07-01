import 'package:bomcurriculo/include/Body.dart';
import 'package:bomcurriculo/widget/Button.dart';
import 'package:flutter/material.dart';

import 'auth/Login.dart';

class Home extends StatefulWidget {
  const Home({
    super.key,
  });
  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {

  void doAction() {

  }

  @override
  Widget build(BuildContext context) {
    return Body(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(30.0),
              child: GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const Login(),
                    ),
                  );
                },
              child: Button(title: 'Login')
                    ),
            ),
          ],
        )
    );
  }
}