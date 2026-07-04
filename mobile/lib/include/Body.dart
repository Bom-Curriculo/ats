import 'package:bomcurriculo/include/Navbar.dart';
import 'package:flutter/material.dart';

class Body extends StatefulWidget {
  const Body({super.key, required this.child});

  final Widget child;

  @override
  _Body createState() => _Body();
}

class _Body extends State<Body> {
  static const double navbarHeight = 50.0;
  bool boolMenu = false;

  @override
  Widget build(BuildContext context) {
    // Por hora as rotas existentes
    // TODO: trocar por links reais no futuro

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: Navbar(
        onMenuChanged: () {
          setState(() {
            boolMenu = !boolMenu;
          });
        },
      ),
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                Expanded(child: SingleChildScrollView(child: widget.child)),
              ],
            ),

            // Menu
          ],
        ),
      ),
    );
  }
}
