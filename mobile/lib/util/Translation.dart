import 'dart:convert';
import 'package:flutter/services.dart';

class Translation {

  static final Translation instance = Translation._();

  Translation._();

  final Map<String, String> _translations = {};

  Future<void> load(String language) async {
    _translations.clear();
    final jsonString = await rootBundle.loadString(
      'assets/translations/$language.json'
    );
    final Map<String,dynamic> json = jsonDecode(jsonString);
    for (final entry in json.entries) {
      _translations[entry.key] = entry.value.toString();
    }
  }

  //Future<String> translate(String text) async {
  String translate(String text) {
    //await Translation.instance.load("pt-BR");
    return _translations[text]??text;
  }

}