
import 'package:bomcurriculo/include/Navbar.dart';
import 'package:flutter/material.dart';

class Body extends StatefulWidget {
  const Body({super.key});
  @override
  _Body createState() => _Body();
}

class _Body extends State<Body> {

  @override
  Widget build(BuildContext context) {

    final media = MediaQuery.of(context);

    return SafeArea(
      child: Stack(
        children: [

          Navbar(),

          Container(
            child: Center(
                child: Text('Hello world')
            ),
          ),

        ],
      ),
    );
  }
}
