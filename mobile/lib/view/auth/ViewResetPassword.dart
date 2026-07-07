import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/util/Translation.dart';
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

  final focusPassword = FocusNode();
  final focusPasswordConfirm = FocusNode();
  final controllerPassword = TextEditingController();
  final controllerPasswordConfirm = TextEditingController();

  String errorText = '';
  String errorPassword='';
  String errorPasswordConfirm='';

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
    focusPassword.requestFocus();
  }

  void doPasswordChange() async {
    bool error = false;

    // Reseta erros
    setState(() {
      errorPassword = '';
      errorPasswordConfirm = '';
    });

    // Valida email
    if (controllerPassword.text=="") {
      errorPassword = Translation.instance.translate('Type your new password');
      focusPassword.requestFocus();
      error = true;
    } else if (controllerPasswordConfirm.text=="") {
      errorPasswordConfirm = Translation.instance.translate('Type your new password again');
      focusPasswordConfirm.requestFocus();
      error = true;
    } else if (controllerPassword.text!=controllerPasswordConfirm.text) {
      errorPasswordConfirm = Translation.instance.translate('Your passwords doesn\'t match');
      focusPasswordConfirm.requestFocus();
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
      var response = await api.post('auth/reset-password', {
        'password': controllerPassword.text,
        'password_confirm': controllerPasswordConfirm.text,
        'otp': widget.otp
      });

      if (response.statusCode==200) {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const ViewLogin()),
        );
      } else if (response.statusCode==422) {
        setState(() {
          errorText = 'Erro ao alterar senha';
        });
      } else {
        setState(() {
          errorText = 'Erro na comunicação com o servidor';
        });
      }

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
            Translation.instance.translate('Type and confirm your password to change'),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 30.0),
          WidgetInputText(
              title: Translation.instance.translate('New password'),
              controller: controllerPassword,
              error: errorPassword,
              focusNode: focusPassword,
              isPassword: true
          ),
          WidgetInputText(
              title: Translation.instance.translate('Retype your password'),
              controller: controllerPasswordConfirm,
              error: errorPasswordConfirm,
              focusNode: focusPasswordConfirm,
              isPassword: true
          ),
          GestureDetector(
            onTap: doPasswordChange,
            child: WidgetButton(title: Translation.instance.translate('Update password')),
          ),
        ],
      ),
    );
  }
}
