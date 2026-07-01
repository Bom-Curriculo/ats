
import 'package:flutter/material.dart';

class Logo extends StatefulWidget {
  const Logo({super.key});
  @override
  _Logo createState() => _Logo();
}

class _Logo extends State<Logo> {



  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 200.0,
          height: 100.0,
          color: Colors.black12,
          child: Center(child: Text('Logo')),
        ),
        SizedBox(height: 45.0)
      ],
    );
  }
}
