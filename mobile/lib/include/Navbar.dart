import 'package:bomcurriculo/service/API.dart';
import 'package:bomcurriculo/util/Translation.dart';
import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/view/auth/ViewLogin.dart';
import 'package:bomcurriculo/view/auth/ViewRegister.dart';
import 'package:bomcurriculo/view/resume/ViewGenerateResume.dart';
import 'package:bomcurriculo/view/resume/ViewNewResume.dart';
import 'package:bomcurriculo/widget/WidgetButtonIcon.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../config.dart';
import '../service/DB.dart';

class Navbar extends StatefulWidget implements PreferredSizeWidget {
  const Navbar({super.key, this.onMenuChanged});

  final VoidCallback? onMenuChanged;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  State<Navbar> createState() => _NavbarState();
}

class _NavbarState extends State<Navbar> {

  @override
  void initState() {
    super.initState();
    getTranslation();
  }

  Future<void> getTranslation() async {
    await Translation.instance.load("pt-BR");
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> logout(BuildContext context) async {
    try {
      var response = await API().get('auth/logout');
      print(response.body);
    } catch (_) {}

    try {
      await DB.instance.clear();
    } catch (_) {}

    context.go("/auth/login");
  }

  @override
  Widget build(BuildContext context) {
    final links = [
      {
        'title': Translation.instance.translate('Home'),
        'widget': const ViewHome(),
      },
      {
        'title': Translation.instance.translate('New resume'),
        'widget': const ViewNewResume(),
      },
      {
        'title': Translation.instance.translate('Generate resume'),
        'widget': const ViewGenerateResume(),
      },
      {
        'title': Translation.instance.translate('Login'),
        'widget': const ViewLogin(),
      },
      {
        'title': Translation.instance.translate('Register'),
        'widget': const ViewRegister(),
      },
      {
        'title': Translation.instance.translate('Logout'),
        'action': () => logout(context),
      },
    ];

    return AppBar(
      backgroundColor: const Color(0xFFEEEEEE),
      elevation: 0,
      automaticallyImplyLeading: false,
      titleSpacing: 11.0,
      title: GestureDetector(
        onTap: () {
          context.go("/");
        },
        child: Text(
          appTitle,
          style: const TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 18.0,
            color: Colors.black,
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

            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => item as Widget),
            );
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