
import 'package:flutter/material.dart';

class Button extends StatefulWidget {
  const Button({
    super.key,
    required this.title
  });
  final String title;
  @override
  _Button createState() => _Button();
}

class _Button extends State<Button> {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: Text(widget.title),
    );
  }
}
