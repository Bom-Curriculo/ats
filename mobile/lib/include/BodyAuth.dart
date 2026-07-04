import 'package:bomcurriculo/include/Navbar.dart';
import 'package:flutter/material.dart';

import '../widget/WidgetLogo.dart';

class BodyAuth extends StatefulWidget {
  const BodyAuth({super.key, required this.child});

  final Widget child;

  @override
  _BodyAuth createState() => _BodyAuth();
}

class _BodyAuth extends State<BodyAuth> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const Navbar(),
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(45.0),
                    child: SingleChildScrollView(child: Column(
                      children: [
                        WidgetLogo(),
                        widget.child,
                      ],
                    )),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
