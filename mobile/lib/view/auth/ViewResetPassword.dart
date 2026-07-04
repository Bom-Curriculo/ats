import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:flutter/material.dart';

import '../../widget/WidgetButton.dart';
import '../../widget/WidgetInputText.dart';

class ViewResetPassword extends StatefulWidget {
  const ViewResetPassword({super.key});
  @override
  _ViewResetPassword createState() => _ViewResetPassword();
}

class _ViewResetPassword extends State<ViewResetPassword> {
  void doPasswordChange() {}

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          Text(
            'Type and confirm your password to change',
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          WidgetInputText(title: 'New password', isPassword: true),
          WidgetInputText(title: 'Retype your password', isPassword: true),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ViewLogin()),
              );
            },
            child: WidgetButton(title: 'Update password'),
          ),
        ],
      ),
    );
  }
}
