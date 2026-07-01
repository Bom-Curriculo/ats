
import 'package:flutter/material.dart';

class ButtonIcon extends StatefulWidget {
  const ButtonIcon({
    super.key,
    required this.icon
  });
  final IconData icon;
  @override
  _ButtonIcon createState() => _ButtonIcon();
}

class _ButtonIcon extends State<ButtonIcon> {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Color(0xFFDDDDDD),
        borderRadius: BorderRadius.circular(4.0)
      ),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Icon(widget.icon),
      ),
    );
  }
}
