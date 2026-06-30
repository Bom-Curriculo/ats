import 'package:bomcurriculo/widget/ButtonIcon.dart';
import 'package:flutter/material.dart';

class Navbar extends StatefulWidget {
  const Navbar({super.key});
  @override
  _Navbar createState() => _Navbar();
}

class _Navbar extends State<Navbar> {
  @override
  Widget build(BuildContext context) {
    return Container(
        width: double.infinity,
        height: 50.0,
        color: Colors.black12,
        child: Row(
          children: [
            SizedBox(width: 10.0),
            Expanded(
                child: Text(
                  'Bom Currículo',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16.0),
                )
            ),
            ButtonIcon(icon: Icons.menu),
            SizedBox(width: 10.0),
          ],
        )
    );
  }
}