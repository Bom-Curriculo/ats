
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
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.blue,
        borderRadius: BorderRadius.circular(4.0),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 25.0),
        child: Center(
          child: Text(
              widget.title,
              style: TextStyle(
                color: Colors.white,
                fontSize: 16.0
              ),
          ),
        ),
      ),
    );
  }
}