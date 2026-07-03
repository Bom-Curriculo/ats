import 'package:bomcurriculo/domain/dto/login_dto.dart';
import 'package:bomcurriculo/repositories/auth_repository.dart';
import 'package:flutter/foundation.dart';

class LoginViewModel extends ChangeNotifier {
  final AuthRepository _repository = AuthRepository();
  Future<void> login(LoginDto dto) async {
    try {
      final token = await _repository.login(dto);

      // salvar token
      print(token);

    } catch (e) {
      rethrow;
    }
  }
}
