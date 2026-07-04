import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:flutter/material.dart';

import '../../widget/WidgetButton.dart';
import '../../widget/WidgetInputText.dart';
import 'ViewVerifyOTP.dart';

class ViewRecovery extends StatefulWidget {
  const ViewRecovery({super.key});
  @override
  _ViewRecovery createState() => _ViewRecovery();
}

class _ViewRecovery extends State<ViewRecovery> {
  void doSendEmail() {}

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          Text(
            'Forgot your password? Type your email to receive OTP code to change your password',
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          WidgetInputText(title: 'Email'),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ViewVerifyOTP()),
              );
            },
            child: WidgetButton(title: 'Recover password'),
          ),
        ],
      ),
    );
  }
}
