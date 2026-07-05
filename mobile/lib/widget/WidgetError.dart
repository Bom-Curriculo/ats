
import 'package:flutter/material.dart';

class WidgetError extends StatefulWidget {
  const WidgetError({
    super.key,
    this.text=''
  });

  final String text;

  @override
  _WidgetError createState() => _WidgetError();
}

class _WidgetError extends State<WidgetError> {



  @override
  Widget build(BuildContext context) {
    return Column(children: [
      widget.text!=""?Container(
        width: double.infinity,
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Center(
              child: Wrap(
                alignment: WrapAlignment.center,
                crossAxisAlignment: WrapCrossAlignment.center,
                spacing: 5,
                children: [
                  Icon(Icons.error, color: Colors.red),
                  SizedBox(width: 5.0),
                  Text(
                      widget.text,
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.red, fontWeight: FontWeight.w600)
                  ),
                ],
              )
          ),
        ),
        decoration: BoxDecoration(
            color: Colors.red[100],
            borderRadius: BorderRadius.circular(4.0)
        ),
      ):SizedBox(),
      SizedBox(height: widget.text!=""?15.0:0),
    ]);
  }
}
