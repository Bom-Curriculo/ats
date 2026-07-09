import 'dart:convert';

import 'package:bomcurriculo/include/BodyAuth.dart';
import 'package:bomcurriculo/util/Translation.dart';
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

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
  }

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
      errorName = Translation.instance.translate('Type your name');
      error = true;
    }

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
    } else if (controllerRetypePassword.text=="") {
      errorRetypePassword=Translation.instance.translate('Retype your password');
      error = true;
    } else if (controllerPassword.text!=controllerRetypePassword.text) {
      errorRetypePassword=Translation.instance.translate('Your password doesn\'t match');
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
          errorName = '';
          errorEmail = '';
          errorPassword='';
          errorText=errorString;
          //errorText=body['message'];
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
              title: Translation.instance.translate('Name'),
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
              title: Translation.instance.translate('Type your password'),
              controller: controllerPassword,
              error: errorPassword,
              isPassword: true,
              maxLength: 64
          ),
          WidgetInputText(
              title: Translation.instance.translate('Retype your password'),
              controller: controllerRetypePassword,
              error: errorRetypePassword,
              isPassword: true,
              maxLength: 64
          ),
          WidgetError(text:errorText),
          GestureDetector(
            onTap: doRegister,
            child: WidgetButton(
                title: loading ? '${Translation.instance.translate('Loading')}...' : Translation.instance.translate('Register'),
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
            child: Text(Translation.instance.translate('Back to login')),
          ),
          SizedBox(height: 15.0),
        ],
      ),
    );
  }
}