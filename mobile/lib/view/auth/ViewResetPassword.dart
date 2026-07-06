import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:flutter/material.dart';

import '../../service/API.dart';
import '../../widget/WidgetButton.dart';
import '../../widget/WidgetInputText.dart';

class ViewResetPassword extends StatefulWidget {
  const ViewResetPassword({
    super.key,
    required this.otp
  });

  final String otp;

  @override
  _ViewResetPassword createState() => _ViewResetPassword();
}

class _ViewResetPassword extends State<ViewResetPassword> {

  bool loading = false;

  final controllerPassword = TextEditingController();
  final controllerPasswordConfirm = TextEditingController();

  String errorPassword='';
  String errorPasswordConfirm='';

  void doPasswordChange() async {
    bool error = false;

    // Reseta erros
    setState(() {
      errorPassword = '';
      errorPasswordConfirm = '';
    });

    // Valida email
    if (controllerPassword.text=="") {
      errorPassword = 'Type your new password';
      error = true;
    } else if (controllerPassword.text=="") {
      errorPasswordConfirm = 'Type your new password again';
      error = true;
    } else if (controllerPassword.text!=controllerPasswordConfirm.text) {
      errorPasswordConfirm = 'Your passwords doesn\'t match';
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
        loading = true;
        errorPassword = '';
        errorPasswordConfirm = '';
      });

      API api = API();
      await api.post('auth/reset-password', {
        'password': controllerPassword.text,
        'password_confirm': controllerPasswordConfirm.text,
        'opt': widget.otp
      });

      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const ViewLogin()),
      );

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
            'Type and confirm your password to change',
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          WidgetInputText(
              title: 'New password',
              controller: controllerPassword,
              error: errorPassword,
              isPassword: true
          ),
          WidgetInputText(
              title: 'Retype your password',
              controller: controllerPasswordConfirm,
              error: errorPasswordConfirm,
              isPassword: true
          ),
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
