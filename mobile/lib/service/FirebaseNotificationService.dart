import 'dart:convert';
import 'dart:io';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:async';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {}

const AndroidNotificationChannel _channel = AndroidNotificationChannel(
  'flower_foreground_channel',
  'Flower Notificações',
  description: 'Canal para exibir notificações enquanto o app está em uso.',
  importance: Importance.high,
);

final FlutterLocalNotificationsPlugin _fln = FlutterLocalNotificationsPlugin();

class NotificationService {
  static final _messaging = FirebaseMessaging.instance;
  static void Function(Map<String, dynamic> data)? onBattleInvite;

  static Future<void> init({
    required void Function(Map<String, dynamic> data) onNotificationTap,
  }) async {
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

    if (Platform.isAndroid) {
      await _messaging.requestPermission();
    }

    const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosInit = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false,
    );

    await _fln.initialize(
      settings: const InitializationSettings(
        android: androidInit,
        iOS: iosInit,
      ),
      onDidReceiveNotificationResponse: (NotificationResponse resp) {
        final payload = resp.payload;
        if (payload != null && payload.isNotEmpty) {
          try {
            onNotificationTap(jsonDecode(payload) as Map<String, dynamic>);
          } catch (_) {
            onNotificationTap({'payload': payload});
          }
        }
      },
    );

    await _fln
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(_channel);

    await _messaging.setForegroundNotificationPresentationOptions(
      alert: true,
      badge: true,
      sound: true,
    );

    final initialMsg = await _messaging.getInitialMessage();
    if (initialMsg?.data.isNotEmpty == true) {
      onNotificationTap(initialMsg!.data);
    }

    FirebaseMessaging.onMessageOpenedApp.listen(
      (msg) => onNotificationTap(msg.data),
    );

    FirebaseMessaging.onMessage.listen((RemoteMessage msg) async {
      final data = msg.data;
      if (data['route'] == '/home-page') {
        // fazer algo
        return;
      }
      final notif = msg.notification;
      if (notif != null) {
        await _fln.show(
          id: notif.hashCode,
          title: notif.title ?? 'Bom Currículo',
          body: notif.body ?? '',
          notificationDetails: NotificationDetails(
            android: AndroidNotificationDetails(
              _channel.id,
              _channel.name,
              channelDescription: _channel.description,
              icon: '@mipmap/ic_launcher',
              priority: Priority.high,
              importance: Importance.high,
            ),
            iOS: const DarwinNotificationDetails(),
          ),
          payload: msg.data.isNotEmpty ? jsonEncode(msg.data) : null,
        );
      }
    });
  }
}
