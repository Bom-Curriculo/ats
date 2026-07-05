import 'dart:convert';

import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/util/Validation.dart';
import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/view/auth/ViewForgotPassword.dart';
import 'package:bomcurriculo/view/auth/ViewRegister.dart';
import 'package:bomcurriculo/widget/WidgetError.dart';
import 'package:flutter/material.dart';

import '../../service/API.dart';
import '../../service/DB.dart';
import '../../widget/WidgetButton.dart';
import '../../widget/WidgetInputText.dart';

class ViewLogin extends StatefulWidget {
  const ViewLogin({super.key});
  @override
  _ViewLogin createState() => _ViewLogin();
}

class _ViewLogin extends State<ViewLogin> {

  bool loading = false;

  final controllerEmail = TextEditingController();
  final controllerPassword = TextEditingController();

  String errorEmail='';
  String errorPassword='';
  String errorText='';

  void doLogin() async {

    bool error = false;

    // Reseta erros
    setState(() {
      errorEmail = '';
      errorPassword='';
      errorText='';
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
        errorText='';
      });

      API api = API();
      var response = await api.post('auth/login', {
        'email': controllerEmail.text,
        'password': controllerPassword.text
      });

      var body =  jsonDecode(response.body);

      if (response.statusCode==200) {
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
              title: 'Email',
              error: errorEmail,
              controller: controllerEmail,
              maxLength: 128
          ),
          WidgetInputText(
              title: 'Password',
              error: errorPassword,
              controller: controllerPassword,
              isPassword: true,
              maxLength: 64
          ),

          WidgetError(text: errorText),

          GestureDetector(
            onTap: doLogin,
            child: WidgetButton(
                title: loading ? 'Loading...' : 'Login',
                color: loading ? Colors.black26 : Colors.blue
            ),
          ),

          SizedBox(height: 30.0),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ViewRegister()),
              );
            },
            child: Text('Signup for free'),
          ),
          SizedBox(height: 15.0),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ViewForgotPassword()),
              );
            },
            child: Text('Forgot password'),
          ),
          SizedBox(height: 15.0),
        ],
      ),
    );
  }
}