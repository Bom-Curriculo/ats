import 'package:bomcurriculo/config.dart';
import 'package:bomcurriculo/routes.dart';
import 'package:bomcurriculo/service/ServiceAuth.dart';
import 'package:flutter/material.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final logged = await ServiceAuth().isLogged();
  runApp(MyApp(logged: logged));
}

class MyApp extends StatelessWidget {

  final bool logged;

  const MyApp({
    super.key,
    required this.logged,
  });

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: createRouter(logged),
      debugShowCheckedModeBanner: false,
      title: appTitle,
      theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple)),
    );
  }
}