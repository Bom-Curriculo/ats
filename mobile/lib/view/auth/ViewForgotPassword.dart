import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/ViewVerifyOTP.dart';
import 'package:flutter/material.dart';

import '../../util/Validation.dart';
import '../../widget/WidgetButton.dart';
import '../../widget/WidgetInputText.dart';

class ViewForgotPassword extends StatefulWidget {
  const ViewForgotPassword({super.key});
  @override
  _ViewForgotPassword createState() => _ViewForgotPassword();
}

class _ViewForgotPassword extends State<ViewForgotPassword> {

  bool loading = false;

  final controllerEmail = TextEditingController();

  String errorEmail='';

  void doSendEmail() {

    bool error = false;

    // Reseta erros
    setState(() {
      errorEmail = '';
    });

    // Valida email
    if (controllerEmail.text=="") {
      errorEmail = 'Type your email';
      error = true;
    } else if (!Validation().isEmail(controllerEmail.text)) {
      errorEmail = 'Incorrect email';
      error = true;
    }

    // Se tiver erro
    if (error) {
      setState((){});
      return;
    }

    // Se não tiver erro
    if (!error) {
      setState(() {
        loading=true;
        errorEmail = '';
      });

      // Faz um delay pra voltar o estado do botão
      // TODO: remover
      Future.delayed(Duration(seconds: 2), () {
        setState(() {
          loading=false;
        });
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const ViewVerifyOTP()),
        );
      });


      /*
      API api = API();
      api.post('auth/login', {
        'email': controllerEmail.text,
        'password': controllerPassword.text
      });
      */

    }

  }

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
          WidgetInputText(
              title: 'Email',
              controller: controllerEmail,
              error: errorEmail,
          ),
          GestureDetector(
            onTap: doSendEmail,
            child: WidgetButton(
                title: loading ? 'Loading...' : 'Recover password',
                color: loading ? Colors.black26 : Colors.blue
            ),
          ),
        ],
      ),
    );
  }
}