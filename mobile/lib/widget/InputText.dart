
import 'package:flutter/material.dart';

class InputText extends StatefulWidget {
  const InputText({
    super.key,
    this.isPassword = false,
    this.title='',
    this.label=''
  });

  final bool isPassword;
  final String title;
  final String? label;

  @override
  _InputText createState() => _InputText();
}

class _InputText extends State<InputText> {

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(widget.title, style: TextStyle(fontSize: 16.0)),
          TextField(
            obscureText: widget.isPassword,
            decoration: InputDecoration(
              labelText: '',
              //border: OutlineInputBorder()
            ),
          ),
          SizedBox(height: 15.0)
        ],
      ),
    );
  }
}
