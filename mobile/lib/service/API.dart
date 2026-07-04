import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config.dart';

class API {

  String? jwt;

  API({this.jwt});

  void setJWT(String token) {
    jwt = token;
  }

  Map<String,String> _headers() {
    final headers = <String, String> {
      "Content-Type": "application/json",
      "Accept": "application/json"
    };

    if (jwt != null && jwt!.isNotEmpty) {
      headers["Authentication"] = "Bearer $jwt";
    }

    return headers;
  }

  Map<dynamic, dynamic> _response(http.Response response) {
    try {
      if (response.body.isNotEmpty) {

        final data = jsonDecode(response.body);

        if (data is Map) {
          return Map<dynamic, dynamic>.from(data);
        }

        return {
          "success": response.statusCode >= 200 && response.statusCode < 300,
          "status": response.statusCode,
          "data": data
        };
      }

      return {
        "success": response.statusCode >= 200 && response.statusCode < 300,
        "status": response.statusCode
      };

    } catch (_) {
      return {
        "success": response.statusCode >= 200 && response.statusCode < 300,
        "status": response.statusCode,
        "message": response.body
      };
    }
  }

  Future<Map<dynamic,dynamic>> get(String url) async {
    try {
      final response = await http.get(
        Uri.parse("$baseURL$url"),
        headers: _headers()
      );
      return _response(response);
    } catch (e) {
      return {
        "success": false,
        "message": e.toString()
      };
    }
  }

  Future<Map<dynamic,dynamic>> post(String url, Map<String,dynamic> data) async {
    try {
      final response = await http.post(
          Uri.parse("$baseURL$url"),
          headers: _headers(),
          body: jsonEncode(data)
      );
      return _response(response);
    } catch (e) {
      return {
        "success": false,
        "message": e.toString()
      };
    }
  }

  Future<Map<dynamic,dynamic>> put(String url, Map<String,dynamic> data) async {
    try {
      final response = await http.put(
          Uri.parse("$baseURL$url"),
          headers: _headers(),
          body: jsonEncode(data)
      );
      return _response(response);
    } catch (e) {
      return {
        "success": false,
        "message": e.toString()
      };
    }
  }

  Future<Map<dynamic,dynamic>> patch(String url, Map<String,dynamic> data) async {
    try {
      final response = await http.patch(
          Uri.parse("$baseURL$url"),
          headers: _headers(),
          body: jsonEncode(data)
      );
      return _response(response);
    } catch (e) {
      return {
        "success": false,
        "message": e.toString()
      };
    }
  }

  Future<Map<dynamic,dynamic>> delete(String url) async {
    try {
      final response = await http.delete(
          Uri.parse("$baseURL$url"),
          headers: _headers()
      );
      return _response(response);
    } catch (e) {
      return {
        "success": false,
        "message": e.toString()
      };
    }
  }

}