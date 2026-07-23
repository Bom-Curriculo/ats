import 'package:bomcurriculo/config.dart';
import 'package:bomcurriculo/routes.dart';
import 'package:bomcurriculo/service/DB.dart';
import 'package:bomcurriculo/service/FirebaseNotificationService.dart';
import 'package:bomcurriculo/service/ServiceAuth.dart';
import 'package:flutter/material.dart';

// Firebase imports
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
final GlobalKey<NavigatorState> _navKey = GlobalKey<NavigatorState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 2. Initialize Firebase
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

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

  await DB.instance.saveFCM(token!);

  final fcm = await DB.instance.getFCM();

  print("##########################");
  print(fcm);
  print("##########################");

  await NotificationService.init(
    onNotificationTap: (data) {
      final route = data['route'] ?? '/';
      // invite vindo de background/terminated (usuário tocou na notificação)
      // if (route == '/home-page') {
      //   abrir tela X...
      // }
      _navKey.currentState?.pushNamed(route, arguments: data);
    },
  );

  final logged = await ServiceAuth().isLogged();
  runApp(MyApp(logged: logged));
}

class MyApp extends StatelessWidget {
  final bool logged;

  const MyApp({super.key, required this.logged});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: createRouter(logged),
      debugShowCheckedModeBanner: false,
      title: appTitle,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
    );
  }
}
