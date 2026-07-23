// O antigo teste de widget (template padrao do `flutter create`) testava um
// contador que nao existe no app real e sempre falhava. Testar o app de
// verdade via WidgetTester exige mockar o sqflite (o Navbar consulta o DB
// local ja no initState, em toda tela), o que fica para um PR futuro com
// sqflite_common_ffi. Por ora cobrimos a validacao de email, unit puro e
// sem dependencia de plataforma.

import 'package:flutter_test/flutter_test.dart';

import 'package:bomcurriculo/util/Validation.dart';

void main() {
  group('Validation.isEmail', () {
    final validation = Validation();

    test('aceita um email valido', () {
      expect(validation.isEmail('usuario@email.com'), isTrue);
    });

    test('rejeita string sem @', () {
      expect(validation.isEmail('usuario-email.com'), isFalse);
    });

    test('rejeita string vazia', () {
      expect(validation.isEmail(''), isFalse);
    });
  });
}
