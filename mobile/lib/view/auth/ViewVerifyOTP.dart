import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/util/Translation.dart';
import 'package:bomcurriculo/view/auth/ViewResetPassword.dart';
import 'package:bomcurriculo/widget/WidgetError.dart';
import 'package:flutter/material.dart';

import '../../service/API.dart';
import '../../widget/WidgetButton.dart';
import '../../widget/WidgetInputText.dart';

class ViewVerifyOTP extends StatefulWidget {
  const ViewVerifyOTP({super.key});
  @override
  _ViewVerifyOTP createState() => _ViewVerifyOTP();
}

class _ViewVerifyOTP extends State<ViewVerifyOTP> {
  String errorText = '';

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

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
    focusOTP1.requestFocus();
  }

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

  void doConfirmOTP() async {
    setState(() {
      errorText = '';
    });

    if (controllerOTP1.text == "" ||
        controllerOTP2.text == "" ||
        controllerOTP3.text == "" ||
        controllerOTP4.text == "" ||
        controllerOTP5.text == "" ||
        controllerOTP6.text == "") {
      //erro
      setState(() {
        errorText = Translation.instance.translate('Invalid OTP');
      });
      return;
    }

    String otp = "";
    otp += controllerOTP1.text;
    otp += controllerOTP2.text;
    otp += controllerOTP3.text;
    otp += controllerOTP4.text;
    otp += controllerOTP5.text;
    otp += controllerOTP6.text;

    API api = API();
    var response = await api.post('auth/verify-otp', {'otp': otp});

    if (response.statusCode == 200) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => ViewResetPassword(otp: otp)),
      );
    } else if (response.statusCode == 422) {
      setState(() {
        errorText = Translation.instance.translate('Invalid OTP');
      });
    } else {
      setState(() {
        errorText = Translation.instance.translate('Server comunication error');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          Text(
            Translation.instance.translate(
              'Type the OTP sent to your email to change your password',
            ),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          Row(
            children: [
              Expanded(
                child: WidgetInputText(
                  controller: controllerOTP1,
                  focusNode: focusOTP1,
                  nextFocusNode: focusOTP2,
                  maxLength: 1,
                  textAlignCenter: true,
                ),
              ),
              SizedBox(width: 5.0),
              Expanded(
                child: WidgetInputText(
                  controller: controllerOTP2,
                  previousController: controllerOTP1,
                  focusNode: focusOTP2,
                  previousFocusNode: focusOTP1,
                  nextFocusNode: focusOTP3,
                  maxLength: 1,
                  textAlignCenter: true,
                ),
              ),
              SizedBox(width: 5.0),
              Expanded(
                child: WidgetInputText(
                  controller: controllerOTP3,
                  previousController: controllerOTP2,
                  focusNode: focusOTP3,
                  previousFocusNode: focusOTP2,
                  nextFocusNode: focusOTP4,
                  maxLength: 1,
                  textAlignCenter: true,
                ),
              ),
              SizedBox(width: 5.0),
              Expanded(
                child: WidgetInputText(
                  controller: controllerOTP4,
                  previousController: controllerOTP3,
                  focusNode: focusOTP4,
                  previousFocusNode: focusOTP3,
                  nextFocusNode: focusOTP5,
                  maxLength: 1,
                  textAlignCenter: true,
                ),
              ),
              SizedBox(width: 5.0),
              Expanded(
                child: WidgetInputText(
                  controller: controllerOTP5,
                  previousController: controllerOTP4,
                  focusNode: focusOTP5,
                  previousFocusNode: focusOTP4,
                  nextFocusNode: focusOTP6,
                  maxLength: 1,
                  textAlignCenter: true,
                ),
              ),
              SizedBox(width: 5.0),
              Expanded(
                child: WidgetInputText(
                  controller: controllerOTP6,
                  previousController: controllerOTP5,
                  focusNode: focusOTP6,
                  previousFocusNode: focusOTP5,
                  maxLength: 1,
                  textAlignCenter: true,
                ),
              ),
            ],
          ),
          WidgetError(text: errorText),
          GestureDetector(
            onTap: doConfirmOTP,
            child: WidgetButton(
              title: Translation.instance.translate('Confirm OTP'),
            ),
          ),
        ],
      ),
    );
  }
}
