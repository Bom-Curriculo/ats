import 'API.dart';

class ServiceAuth {
  Future<bool> isLogged() async {
    try {
      API api = API();
      final response = await api.get("client/user");
      return response.statusCode == 200;
    } catch (_) {
      //await DB.instance.clear();
      return false;
    }
  }

  Future<bool> login() async {
    return false;
  }

  register() {}

  Future<bool> logout() async {
    return false;
  }

  forgotPassword() {}

  verifyOTP() {}

  resetPassword() {}
}
