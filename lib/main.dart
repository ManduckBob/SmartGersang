import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter/services.dart';

// 🔹 백그라운드 푸시 메시지 처리
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print("📨 백그라운드 메시지 수신: ${message.messageId}");
}

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

  const AndroidInitializationSettings initializationSettingsAndroid =
      AndroidInitializationSettings('@mipmap/ic_launcher');

  const InitializationSettings initializationSettings = InitializationSettings(
    android: initializationSettingsAndroid,
  );

  await flutterLocalNotificationsPlugin.initialize(initializationSettings);

  // ✅ 상태표시줄 블랙 + 흰색 아이콘 설정
  SystemChrome.setSystemUIOverlayStyle(
    SystemUiOverlayStyle(
      statusBarColor: Colors.black,
      statusBarIconBrightness: Brightness.light,
      statusBarBrightness: Brightness.dark,
    ),
  );

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: WebAppPage(),
    );
  }
}

class WebAppPage extends StatefulWidget {
  const WebAppPage({super.key});

  @override
  State<WebAppPage> createState() => _WebAppPageState();
}

class _WebAppPageState extends State<WebAppPage> {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;

  @override
  void initState() {
    super.initState();
    print("🔥 initState 호출됨");
    _setupFCM();
  }

  void _setupFCM() async {
    print("⚙️ _setupFCM 시작됨");

    NotificationSettings settings =
        await _firebaseMessaging.requestPermission();

    print("🔐 권한 상태: ${settings.authorizationStatus}");

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('🔔 알림 권한 허용됨');

      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        print("📥 포그라운드 메시지 수신: ${message.notification?.title}");
      });

      final fcmToken = await _firebaseMessaging.getToken();
      if (fcmToken != null) {
        print("📱 FCM 토큰: $fcmToken");
      } else {
        print("❌ FCM 토큰을 가져오지 못했어요.");
      }
    } else {
      print("🚫 알림 권한이 거부됨");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: InAppWebView(
          initialUrlRequest: URLRequest(
            url: WebUri("https://smartgersang.onrender.com"),
          ),
        ),
      ),
    );
  }
}
