import 'package:bomcurriculo/include/Navbar.dart';
import 'package:bomcurriculo/view/Home.dart';
import 'package:bomcurriculo/view/SendData.dart';
import 'package:bomcurriculo/view/auth/Login.dart';
import 'package:bomcurriculo/view/auth/VerifyOTP.dart';
import 'package:bomcurriculo/view/auth/ResetPassword.dart';
import 'package:bomcurriculo/view/auth/ForgotPassword.dart';
import 'package:bomcurriculo/view/auth/Register.dart';
import 'package:flutter/material.dart';

class Body extends StatefulWidget {
  const Body({
    super.key,
    required this.child
  });

  final Widget child;

  @override
  _Body createState() => _Body();
}

class _Body extends State<Body> {

  static const double navbarHeight = 50.0;
  bool boolMenu = false;

  @override
  Widget build(BuildContext context) {

    // Por hora as rotas existentes
    // TODO: trocar por links reais no futuro
    var links=[
      {
        'title': 'Home',
        'widget': Home()
      },
      {
        'title': 'Send data',
        'widget': SendData()
      },
      {
        'title': 'Login',
        'widget': Login()
      },
      {
        'title': 'Register',
        'widget': Register()
      },
      {
        'title': 'Recovery',
        'widget': ForgotPassword()
      },
      {
        'title': 'OTP',
        'widget': VerifyOTP()
      },
      {
        'title': 'Password',
        'widget': ResetPassword()
      },
      {
        'title': 'Sair',
        'widget': Login()
      }
    ];

    Widget MenuLink(text) {
      return Column(
        children: [
          GestureDetector(
            onTap: () {
              boolMenu=false;
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => text['widget'],
                ),
              );
            },
            child: Container(
              width: double.infinity,
              color: Colors.white,
              child: Padding(
                padding: const EdgeInsets.all(15.0),
                child: Text(text['title']),
              ),
            ),
          ),
          SizedBox(height: 1)
        ],
      );
    }

    return Scaffold(
      backgroundColor: Colors.white,
        body: SafeArea(
        child: Stack(
          children: [

            Column(
              children: [
                Navbar(
                  onMenuChanged: () {
                    setState(() {
                      boolMenu=!boolMenu;
                    });
                  }
                ),
                Expanded(
                    child: SingleChildScrollView(
                        child: widget.child
                    )
                )
              ],
            ),

            // Menu
            AnimatedPositioned(
              duration: Duration(milliseconds: 100),
              top: navbarHeight,
              right: boolMenu?0:-180,
              //bottom: 0,
              width: 180,
              child: Container(
                  color: Color(0xFFEEEEEE),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 1.0),
                    child: Column(children: links.map((link){
                      return MenuLink(link);
                    }).toList()),
                  ),
                ),
              ),
          ],
        ),
      )
    );
  }
}