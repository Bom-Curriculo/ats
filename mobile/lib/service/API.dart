import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config.dart';
import 'DB.dart';

class API {

  Future<Map<String,String>> _headers() async {
    final headers = <String, String> {
      "Content-Type": "application/json",
      "Accept": "application/json"
    };

    String? jwt = await DB.instance.getJWT();
    if (jwt != null && jwt.isNotEmpty) {
      headers["Authentication"] = "Bearer $jwt";
    }

    return headers;
  }

  Future get(String url) async {
    try {
      final response = await http.get(
        Uri.parse("$baseURL$url"),
        headers: await _headers()
      );
      return response;
    } catch (e) {
      return {
        "error": e.toString()
      };
    }
  }

  Future post(String url, Map<String,dynamic> data) async {
    try {
      final response = await http.post(
          Uri.parse("$baseURL$url"),
          headers: await _headers(),
          body: jsonEncode(data)
      );
      return response;
    } catch (e) {
      return {
        "error": e.toString()
      };
    }
  }

  Future put(String url, Map<String,dynamic> data) async {
    try {
      final response = await http.put(
          Uri.parse("$baseURL$url"),
          headers: await _headers(),
          body: jsonEncode(data)
      );
      return response;
    } catch (e) {
      return {
        "error": e.toString()
      };
    }
  }

  Future patch(String url, Map<String,dynamic> data) async {
    try {
      final response = await http.patch(
          Uri.parse("$baseURL$url"),
          headers: await _headers(),
          body: jsonEncode(data)
      );
      return response;
    } catch (e) {
      return {
        "error": e.toString()
      };
    }
  }

  Future delete(String url) async {
    try {
      final response = await http.delete(
          Uri.parse("$baseURL$url"),
          headers: await _headers()
      );
      return response;
    } catch (e) {
      return {
        "error": e.toString()
      };
    }
  }

}