import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

import '../config.dart';
import 'DB.dart';

class API {
  Future<Map<String, String>> _headers() async {
    final headers = <String, String>{
      "Content-Type": "application/json",
      "Accept": "application/json",
    };

    String? jwt = await DB.instance.getJWT();
    if (jwt != null && jwt.isNotEmpty) {
      headers["Authorization"] = "Bearer $jwt";
    }

    debugPrint("Headers: $headers");

    return headers;
  }

  Future get(String url) async {
    try {
      final response = await http.get(
        Uri.parse("$baseURL$url"),
        headers: await _headers(),
      );
      debugPrint("Response: ${response.body}");
      return response;
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  Future post(String url, Map<String, dynamic> data) async {
    try {
      final response = await http.post(
        Uri.parse("$baseURL$url"),
        headers: await _headers(),
        body: jsonEncode(data),
      );
      debugPrint("Response: ${response.body}");
      return response;
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  Future put(String url, Map<String, dynamic> data) async {
    try {
      final response = await http.put(
        Uri.parse("$baseURL$url"),
        headers: await _headers(),
        body: jsonEncode(data),
      );
      debugPrint("Response: ${response.body}");
      return response;
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  Future patch(String url, Map<String, dynamic> data) async {
    try {
      final response = await http.patch(
        Uri.parse("$baseURL$url"),
        headers: await _headers(),
        body: jsonEncode(data),
      );
      debugPrint("Response: ${response.body}");
      return response;
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  Future delete(String url) async {
    try {
      final response = await http.delete(
        Uri.parse("$baseURL$url"),
        headers: await _headers(),
      );
      debugPrint("Response: ${response.body}");
      return response;
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  Future<dynamic> upload(
    String url,
    Map<String, String> data,
    List<Map<String, String>> files,
  ) async {
    try {
      final request = http.MultipartRequest("POST", Uri.parse("$baseURL$url"));

      final headers = await _headers();
      headers.remove("Content-Type");

      request.headers.addAll(headers);
      request.fields.addAll(data);

      // Adiciona os arquivos ao multipart
      for (final file in files) {
        request.files.add(
          await http.MultipartFile.fromPath(file["field"]!, file["path"]!),
        );
      }

      // Envia a requisição
      final streamedResponse = await request.send();

      // Converte para Response normal
      final response = await http.Response.fromStream(streamedResponse);

      // Logs
      debugPrint("Status Code: ${response.statusCode}");
      debugPrint("Response Body: ${response.body}");

      return response;
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  Future<File> download(
    String url, {
    String? fileName,
    Map<String, String>? headers,
  }) async {
    // Faz o download
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode != 200) {
      throw Exception("Erro ao baixar arquivo (${response.statusCode})");
    }

    // Descobre o nome do arquivo
    String name = fileName ?? path.basename(Uri.parse(url).path);

    // Caso a URL não tenha nome de arquivo
    if (name.isEmpty) {
      name = "download";
    }

    // Pasta de documentos do app
    final directory = await getApplicationDocumentsDirectory();

    // Caminho final
    final file = File(path.join(directory.path, name));

    // Garante que a pasta exista
    await file.parent.create(recursive: true);

    // Salva o arquivo
    await file.writeAsBytes(response.bodyBytes);

    debugPrint("Arquivo salvo em: ${file.path}");

    return file;
  }
}
