
import 'package:flutter/material.dart';

class WidgetButton extends StatefulWidget {
  const WidgetButton({
    super.key,
    required this.title,
    this.color = Colors.blue
  });

  final String title;
  final Color color;

  @override
  _WidgetButton createState() => _WidgetButton();
}

class _WidgetButton extends State<WidgetButton> {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: widget.color,
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