import 'package:bomcurriculo/include/Body.dart';
import 'package:flutter/material.dart';

class Home extends StatefulWidget {
  const Home({super.key, required this.title});
  final String title;
  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {

  void doAction() {

  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Body(),
      floatingActionButton: FloatingActionButton(
        onPressed: doAction,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}