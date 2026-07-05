import 'dart:convert';

import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:flutter/material.dart';

import '../../service/API.dart';
import '../../service/DB.dart';
import '../../util/Validation.dart';
import '../../widget/WidgetButton.dart';
import '../../widget/WidgetError.dart';
import '../../widget/WidgetInputText.dart';

class ViewRegister extends StatefulWidget {
  const ViewRegister({super.key});
  @override
  _ViewRegister createState() => _ViewRegister();
}

class _ViewRegister extends State<ViewRegister> {

  bool loading = false;

  final controllerName = TextEditingController();
  final controllerEmail = TextEditingController();
  final controllerPassword = TextEditingController();
  final controllerRetypePassword = TextEditingController();

  String errorName='';
  String errorEmail='';
  String errorPassword='';
  String errorRetypePassword='';
  String errorText='';

  void doRegister() async {

    bool error = false;

    // Reseta erros
    setState(() {
      errorName = '';
      errorEmail = '';
      errorPassword='';
      errorRetypePassword='';
      errorText = '';
    });

    // Valida nome
    if (controllerName.text=="") {
      errorName = 'Type your name';
      error = true;
    }

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
        errorName = '';
        errorEmail = '';
        errorPassword='';
        errorRetypePassword='';
        errorText = '';
      });

      API api = API();
      var response = await api.post('auth/register', {
        'name': controllerName.text,
        'email': controllerEmail.text,
        'password': controllerPassword.text,
        'password_confirm': controllerRetypePassword.text
      });

      var body = jsonDecode(response.body);

      if (response.statusCode==201) {
        if (body['data']['token']!="") {
          await DB.instance.saveJWT(body['data']['token']);
        }
        String user = jsonEncode(body['data']['user']);
        await DB.instance.saveUser(user);
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const ViewHome()),
        );
      } else {
        print(body);
        setState(() {
          loading=false;
          errorName = '';
          errorEmail = '';
          errorPassword='';
          errorText=body['message'];
        });
      }

    }

  }

  @override
  Widget build(BuildContext context) {
    return BodyAuth(
      child: Column(
        children: [
          WidgetInputText(
              title: 'Name',
              controller: controllerName,
              error: errorName,
              maxLength: 128
          ),
          WidgetInputText(
              title: 'Email',
              controller: controllerEmail,
              error: errorEmail,
              maxLength: 64
          ),
          WidgetInputText(
              title: 'Type your password',
              controller: controllerPassword,
              error: errorPassword,
              isPassword: true,
              maxLength: 64
          ),
          WidgetInputText(
              title: 'Retype your password',
              controller: controllerRetypePassword,
              error: errorRetypePassword,
              isPassword: true,
              maxLength: 64
          ),

          WidgetError(text:errorText),

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