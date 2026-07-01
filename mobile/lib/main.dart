import 'package:bomcurriculo/view/Home.dart';
import 'package:bomcurriculo/view/auth/Login.dart';
import 'package:bomcurriculo/view/auth/Password.dart';
import 'package:bomcurriculo/view/auth/Recovery.dart';
import 'package:bomcurriculo/view/auth/Signup.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Bom Currículo',
      theme: ThemeData(
        colorScheme: .fromSeed(seedColor: Colors.deepPurple),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const Home(),
        '/login': (context) => const Login(),
        '/signup': (context) => const Signup(),
        '/recovery': (context) => const Recovery(),
        '/password': (context) => const Password(),
      }
    );
  }
}


