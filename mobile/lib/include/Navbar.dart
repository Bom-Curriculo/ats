import 'package:bomcurriculo/service/API.dart';
import 'package:bomcurriculo/util/Translation.dart';
import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/view/auth/ViewForgotPassword.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:bomcurriculo/view/auth/ViewRegister.dart';
import 'package:bomcurriculo/view/resume/ViewGenerateResume.dart';
import 'package:bomcurriculo/view/resume/ViewNewResume.dart';
import 'package:bomcurriculo/widget/WidgetButtonIcon.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../config.dart';
import '../service/DB.dart';
import '../theme/AppColors.dart';

class Navbar extends StatefulWidget implements PreferredSizeWidget {
  const Navbar({super.key, this.onMenuChanged});

  final VoidCallback? onMenuChanged;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  State<Navbar> createState() => _NavbarState();
}

class _NavbarState extends State<Navbar> {
  bool isLogged = false;

  @override
  void initState() {
    super.initState();
    getTranslation();
    getLogged();
  }

  Future<void> getTranslation() async {
    await Translation.instance.load("pt-BR");
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> getLogged() async {
    final jwt = await DB.instance.getJWT();

    //print("-----------------------------");
    //print(jwt);
    //print("-----------------------------");

    if (jwt == null) {
      isLogged = false;
    } else {
      isLogged = true;
    }
    setState(() {});
  }

  Future<void> logout(BuildContext context) async {
    try {
      final fcm = await DB.instance.getFCM();
      var response = await API().post('auth/logout', {?fcm: fcm});
      print(response.body);
    } catch (_) {}

    try {
      await DB.instance.clear();
    } catch (_) {}

    await getLogged();

    context.go("/auth/login");
    /*
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const ViewLogin(),
      ),
    );
     */
  }

  @override
  Widget build(BuildContext context) {
    var links = [];

    if (!isLogged) {
      links = [
        {
          'title': Translation.instance.translate('Login'),
          'widget': const ViewLogin(),
          'action': () async => context.go("/auth/login"),
        },
        {
          'title': Translation.instance.translate('Register'),
          'widget': const ViewRegister(),
          'action': () async => context.go("/auth/register"),
        },
        {
          'title': Translation.instance.translate('Forgot password'),
          'widget': const ViewForgotPassword(),
          'action': () async => context.go("/auth/forgot-password"),
        },
      ];
    } else {
      links = [
        {
          'title': Translation.instance.translate('Home'),
          'widget': const ViewHome(),
          'action': () async => context.go("/"),
        },
        {
          'title': Translation.instance.translate('New resume'),
          'widget': const ViewNewResume(),
          'action': () async => context.go("/resume/new-resume"),
        },
        {
          'title': Translation.instance.translate('Generate resume'),
          'widget': const ViewGenerateResume(),
          'action': () async => context.go("/resume/generate-resume"),
        },
        {
          'title': Translation.instance.translate('Logout'),
          'action': () async => await logout(context),
        },
      ];
    }

    return AppBar(
      backgroundColor: const Color(0xFFEEEEEE),
      elevation: 0,
      automaticallyImplyLeading: false,
      titleSpacing: 11.0,
      title: GestureDetector(
        onTap: () {
          if (isLogged) {
            context.go("/");
          } else {
            context.go("/auth/login");
          }
          //Navigator.push(
          //  context,
          //  MaterialPageRoute(
          //    builder: (context) => isLogged?ViewHome():ViewLogin(),
          //  ),
          //);
        },
        child: Text(
          appTitle,
          style: const TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 25.0,
            color: AppColorsLight.brandPrimary,
            //color: Colors.black,
          ),
        ),
      ),
      actions: [
        PopupMenuButton<dynamic>(
          icon: const WidgetButtonIcon(
            icon: Icons.menu,
            color: Color(0xFFDDDDDD),
          ),
          onSelected: (item) {
            if (item is Function) {
              item();
              return;
            }
            //Navigator.push(
            //  context,
            //  MaterialPageRoute(builder: (_) => item as Widget),
            //);
          },
          itemBuilder: (BuildContext context) {
            return links.map((link) {
              return PopupMenuItem<dynamic>(
                value: link['action'] ?? link['widget'],
                child: Text(link['title'] as String),
              );
            }).toList();
          },
        ),
        const SizedBox(width: 5.0),
      ],
    );
  }
}
