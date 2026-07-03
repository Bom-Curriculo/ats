import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/ui/auth/reset_password/reset_password.dart';
import 'package:flutter/material.dart';

import '../../../widget/Button.dart';
import '../../../widget/InputText.dart';
import '../../../widget/Logo.dart';

class VerifyOTP extends StatefulWidget {
  const VerifyOTP({super.key});
  @override
  _VerifyOTP createState() => _VerifyOTP();
}

class _VerifyOTP extends State<VerifyOTP> {

  final controllerOTP1 = TextEditingController();
  final controllerOTP2 = TextEditingController();
  final controllerOTP3 = TextEditingController();
  final controllerOTP4 = TextEditingController();
  final controllerOTP5 = TextEditingController();
  final controllerOTP6 = TextEditingController();

  final focusOTP1 = FocusNode();
  final focusOTP2 = FocusNode();
  final focusOTP3 = FocusNode();
  final focusOTP4 = FocusNode();
  final focusOTP5 = FocusNode();
  final focusOTP6 = FocusNode();

  @override
  void dispose() {

    controllerOTP1.dispose();
    controllerOTP2.dispose();
    controllerOTP3.dispose();
    controllerOTP4.dispose();
    controllerOTP5.dispose();
    controllerOTP6.dispose();

    focusOTP1.dispose();
    focusOTP2.dispose();
    focusOTP3.dispose();
    focusOTP4.dispose();
    focusOTP5.dispose();
    focusOTP6.dispose();

    super.dispose();

  }

  void doConfirmOTP() {}

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          Logo(),
          Text(
            'Type the OTP sent to your email to change your password',
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          Row(
            children: [
              Expanded(child: InputText(
                controller: controllerOTP1,
                focusNode: focusOTP1,
                nextFocusNode: focusOTP2,
                maxLength: 1,
                textAlignCenter: true
              )),
              SizedBox(width: 5.0),
              Expanded(child: InputText(
                controller: controllerOTP2,
                previousController: controllerOTP1,
                focusNode: focusOTP2,
                previousFocusNode: focusOTP1,
                nextFocusNode: focusOTP3,
                maxLength: 1,
                textAlignCenter: true
              )),
              SizedBox(width: 5.0),
              Expanded(child: InputText(
                controller: controllerOTP3,
                previousController: controllerOTP2,
                focusNode: focusOTP3,
                previousFocusNode: focusOTP2,
                nextFocusNode: focusOTP4,
                maxLength: 1,
                textAlignCenter: true
              )),
              SizedBox(width: 5.0),
              Expanded(child: InputText(
                controller: controllerOTP4,
                previousController: controllerOTP3,
                focusNode: focusOTP4,
                previousFocusNode: focusOTP3,
                nextFocusNode: focusOTP5,
                maxLength: 1,
                textAlignCenter: true
              )),
              SizedBox(width: 5.0),
              Expanded(child: InputText(
                controller: controllerOTP5,
                previousController: controllerOTP4,
                focusNode: focusOTP5,
                previousFocusNode: focusOTP4,
                nextFocusNode: focusOTP6,
                maxLength: 1,
                textAlignCenter: true
              )),
              SizedBox(width: 5.0),
              Expanded(child: InputText(
                controller: controllerOTP6,
                previousController: controllerOTP5,
                focusNode: focusOTP6,
                previousFocusNode: focusOTP5,
                maxLength: 1,
                textAlignCenter: true
              )),
            ],
          ),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ResetPassword()),
              );
            },
            child: Button(title: 'Confirm OTP'),
          ),
        ],
      ),
    );
  }
}
