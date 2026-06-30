
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
      child: Icon(widget.icon),
    );
  }
}
