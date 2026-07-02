
import 'package:flutter/material.dart';

class ButtonIcon extends StatefulWidget {
  const ButtonIcon({
    super.key,
    required this.icon,
    this.color = const Color(0xFFDDDDDD),
    this.iconColor = const Color(0xFF555555)
  });
  final IconData icon;
  final Color color;
  final Color iconColor;
  @override
  _ButtonIcon createState() => _ButtonIcon();
}

class _ButtonIcon extends State<ButtonIcon> {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: widget.color,
        borderRadius: BorderRadius.circular(4.0)
      ),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Icon(widget.icon, color: widget.iconColor),
      ),
    );
  }
}