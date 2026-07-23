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

  void register() {}

  Future<bool> logout() async {
    return false;
  }

  void forgotPassword() {}

  void verifyOTP() {}

  void resetPassword() {}
}
