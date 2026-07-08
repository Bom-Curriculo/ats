import 'package:bomcurriculo/config.dart';
import 'package:bomcurriculo/routes.dart';
import 'package:bomcurriculo/service/ServiceAuth.dart';
import 'package:flutter/material.dart';
// 1. Add Firebase imports
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'package:firebase_messaging/firebase_messaging.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 2. Initialize Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // Dentro do seu main(), após await Firebase.initializeApp(...)
  final messaging = FirebaseMessaging.instance;

  // 1. Solicita permissão de notificação (obrigatório para iOS e Android 13+)
  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );

  // 2. Recupera o token único do seu aparelho de teste
  String? token = await messaging.getToken();
  print("FCM Token do Aparelho: $token");


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