import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:flutter/material.dart';

import '../../util/Validation.dart';
import '../../widget/WidgetButton.dart';
import '../../widget/WidgetInputText.dart';

class ViewRegister extends StatefulWidget {
  const ViewRegister({super.key});
  @override
  _ViewRegister createState() => _ViewRegister();
}

class _ViewRegister extends State<ViewRegister> {

  bool loading = false;

  final controllerEmail = TextEditingController();
  final controllerPassword = TextEditingController();
  final controllerRetypePassword = TextEditingController();

  String errorEmail='';
  String errorPassword='';
  String errorRetypePassword='';

  void doRegister() {

    bool error = false;

    // Reseta erros
    setState(() {
      errorEmail = '';
      errorPassword='';
      errorRetypePassword='';
    });

    // Valida email
    if (controllerEmail.text=="") {
      errorEmail = 'Type your email';
      error = true;
    } else if (!Validation().isEmail(controllerEmail.text)) {
      errorEmail = 'Incorrect email';
      error = true;
    }

    // Valida senha
    if (controllerPassword.text=="") {
      errorPassword='Type your password';
      error = true;
    } else if (controllerRetypePassword.text=="") {
      errorRetypePassword='Retype your password';
      error = true;
    } else if (controllerPassword.text!=controllerRetypePassword.text) {
      errorRetypePassword='Your password doesn\'t match';
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
        errorPassword='';
        errorRetypePassword='';
      });

      // Faz um delay pra voltar o estado do botão
      // TODO: remover
      Future.delayed(Duration(seconds: 2), () {
        setState(() {
          loading=false;
        });
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const ViewLogin()),
        );
      });

      /*
      API api = API();
      api.post('auth/register', {
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
          WidgetInputText(
              title: 'Email',
              controller: controllerEmail,
              error: errorEmail
          ),
          WidgetInputText(
              title: 'Type your password',
              controller: controllerPassword,
              error: errorPassword,
              isPassword: true
          ),
          WidgetInputText(
              title: 'Retype your password',
              controller: controllerRetypePassword,
              error: errorRetypePassword,
              isPassword: true
          ),
          GestureDetector(
            onTap: doRegister,
            child: WidgetButton(
                title: loading ? 'Loading...' : 'Register',
                color: loading ? Colors.black26 : Colors.blue
            ),
          ),
          SizedBox(height: 30.0),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ViewLogin()),
              );
            },
            child: Text('Back to login'),
          ),
          SizedBox(height: 15.0),
        ],
      ),
    );
  }
}