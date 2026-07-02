import 'package:flutter/material.dart';

class InputText extends StatefulWidget {
  const InputText({
    super.key,
    this.isPassword = false,
    this.title='',
    this.label='',
    this.httpsPrefix='',
    this.controller
  });

  final bool isPassword;
  final String title;
  final String? label;
  final String? httpsPrefix;
  final TextEditingController? controller;

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
          SizedBox(height: 5.0),
          Container(
            decoration: BoxDecoration(
              color: Color(0xFFEEEEEE),
              borderRadius: BorderRadius.circular(4.0)
            ),
            child: TextField(
              controller: widget.controller,
              obscureText: widget.isPassword,
              decoration: InputDecoration(
                prefixText: widget.httpsPrefix,
                isDense: true,
                //labelText: '',
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12.0,
                  vertical: 12.0
                )
                //border: OutlineInputBorder()
              ),
            ),
          ),
          SizedBox(height: 15.0)
        ],
      ),
    );
  }
}