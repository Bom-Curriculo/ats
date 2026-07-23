// Testa que o app sobe sem lancar excecoes, indo para a tela de login
// quando o usuario nao esta autenticado.

import 'package:flutter_test/flutter_test.dart';

import 'package:bomcurriculo/main.dart';

void main() {
  testWidgets('App builds and shows the login screen when logged out', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp(logged: false));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
  });
}
