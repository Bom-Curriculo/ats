import 'package:bomcurriculo/domain/dto/login_dto.dart';
import 'package:dio/dio.dart';

class AuthRepository {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: "http://localhost:8000/api",
      headers: {
        "Content-Type": "application/json",
      },
    ),
  );

  Future<String> login(LoginDto dto) async {
    try {
      final response = await _dio.post(
        "/auth/login",
        data: {
          "email": dto.email,
          "password": dto.password,
        },
      );

      return response.data["token"] as String;
    } on DioException catch (e) {
      if (e.response != null) {
        throw Exception(
          e.response?.data["message"] ?? "Login inválido",
        );
      }

      throw Exception("Erro ao conectar com o servidor.");
    }
  }
}