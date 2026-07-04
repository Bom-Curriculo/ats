
import 'package:flutter/material.dart';

import '../config.dart';

class WidgetLogo extends StatefulWidget {
  const WidgetLogo({super.key});
  @override
  _WidgetLogo createState() => _WidgetLogo();
}

class _WidgetLogo extends State<WidgetLogo> {



  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          //width: 200.0,
          //height: 100.0,
          //color: Colors.black12,
          child: Center(child: Text(
              appTitle,
              style: TextStyle(
                  fontSize: 28.0,
                  fontWeight: FontWeight.w900
              )
            )
          ),
        ),
        SizedBox(height: 45.0)
      ],
    );
  }
}
