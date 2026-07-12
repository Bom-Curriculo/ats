import 'dart:convert';

import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/util/Validation.dart';
import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/view/auth/ViewForgotPassword.dart';
import 'package:bomcurriculo/view/auth/ViewRegister.dart';
import 'package:bomcurriculo/widget/WidgetError.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../service/API.dart';
import '../../service/DB.dart';
import '../../util/Translation.dart';
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

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
  }

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
      errorEmail = Translation.instance.translate('Type your email');
      error = true;
    } else if (!Validation().isEmail(controllerEmail.text)) {
      errorEmail = Translation.instance.translate('Incorrect email');
      error = true;
    }

    // Valida senha
    if (controllerPassword.text=="") {
      errorPassword=Translation.instance.translate('Type your password');
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

      final fcm = await DB.instance.getFCM();

      API api = API();
      var payload = {
        'email': controllerEmail.text,
        'password': controllerPassword.text,
        'fcm': fcm
      };
      print("**********************************");
      print(payload);
      print("**********************************");
      var response = await api.post('auth/login', payload);

      var body =  jsonDecode(response.body);

      if (response.statusCode==200) {
        if (body['data']['token']!="") {
          await DB.instance.saveJWT(body['data']['token']);
        }
        String user = jsonEncode(body['data']['user']);
        await DB.instance.saveUser(user);

        context.go("/");
        //Navigator.push(
        //  context,
        //  MaterialPageRoute(builder: (context) => const ViewHome()),
        //);
      } else if (response.statusCode==422) {

        final Map<String, dynamic> errors = body['data']['errors'];

        final List<String> messages = [];

        errors.forEach((key, value) {
          if (value is List) {
            messages.addAll(value.map((e) => e.toString()));
          } else if (value != null) {
            messages.add(value.toString());
          }
        });

        final errorString = messages.join('\n');

        setState(() {
          loading=false;
          errorEmail = '';
          errorPassword='';
          //errorText=body['message'];
          errorText=errorString;
        });
      } else {
        setState(() {
          loading=false;
          errorEmail = '';
          errorPassword='';
          //errorText=body['message'];
          errorText='';
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
              title: Translation.instance.translate('Password'),
              error: errorPassword,
              controller: controllerPassword,
              isPassword: true,
              maxLength: 64
          ),

          WidgetError(text: errorText),

          GestureDetector(
            onTap: doLogin,
            child: WidgetButton(
                title: loading ? '${Translation.instance.translate('Loading')}...' : Translation.instance.translate('Login'),
                color: loading ? Colors.black26 : Colors.blue
            ),
          ),

          SizedBox(height: 30.0),
          GestureDetector(
            onTap: () {
              context.go("/auth/register");
              //Navigator.push(
              //  context,
              //  MaterialPageRoute(builder: (context) => const ViewRegister()),
              //);
            },
            child: Text(Translation.instance.translate('Signup for free')),
          ),
          SizedBox(height: 15.0),
          GestureDetector(
            onTap: () {
              context.go("/auth/forgot-passwor");
              //Navigator.push(
              //  context,
              //  MaterialPageRoute(builder: (context) => const ViewForgotPassword()),
              //);
            },
            child: Text(Translation.instance.translate('Forgot password')),
          ),
          SizedBox(height: 15.0),
        ],
      ),
    );
  }
}