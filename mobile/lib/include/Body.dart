
import 'package:bomcurriculo/include/Navbar.dart';
import 'package:flutter/material.dart';

class Body extends StatefulWidget {
  const Body({
    super.key,
    required this.child
  });

  final Widget child;

  @override
  _Body createState() => _Body();
}

class _Body extends State<Body> {

  @override
  Widget build(BuildContext context) {

    final media = MediaQuery.of(context);

    return Scaffold(
        body: SafeArea(
        child: Column(
          children: [

            Navbar(),

            widget.child
          ],
        ),
      )
    );
  }
}
