import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/util/Translation.dart';
import 'package:bomcurriculo/view/auth/ViewVerifyOTP.dart';
import 'package:bomcurriculo/widget/WidgetError.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../service/API.dart';

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

  final FocusNode focusEmail = FocusNode();
  final controllerEmail = TextEditingController();

  String errorEmail = '';
  String errorText = '';

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
    focusEmail.requestFocus();
  }

  void doSendEmail() async {
    bool error = false;

    // Reseta erros
    setState(() {
      errorEmail = '';
      errorText = '';
    });

    // Valida email
    if (controllerEmail.text == "") {
      errorEmail = Translation.instance.translate('Type your email');
      error = true;
    } else if (!Validation().isEmail(controllerEmail.text)) {
      errorEmail = Translation.instance.translate('Incorrect email');
      error = true;
    }

    // Se tiver erro
    if (error) {
      setState(() {});
      return;
    }

    // Se não tiver erro
    if (!error) {
      setState(() {
        loading = true;
        errorEmail = '';
        errorText = '';
      });

      API api = API();
      await api.post('auth/forgot-password', {'email': controllerEmail.text});

      context.go("/auth/verify-otp");
      //Navigator.push(
      //  context,
      //  MaterialPageRoute(builder: (context) => const ViewVerifyOTP()),
      //);

      setState(() {
        loading = false;
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
              'Forgot your password? Type your email to receive OTP code to change your password',
            ),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          WidgetInputText(
            title: 'Email',
            controller: controllerEmail,
            error: errorEmail,
            focusNode: focusEmail,
          ),
          WidgetError(text: errorText),
          GestureDetector(
            onTap: doSendEmail,
            child: WidgetButton(
              title: loading
                  ? '${Translation.instance.translate('Loading')}...'
                  : Translation.instance.translate('Recover password'),
              color: loading ? Colors.black26 : Colors.blue,
            ),
          ),
        ],
      ),
    );
  }
}
