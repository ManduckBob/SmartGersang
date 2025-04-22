import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter/services.dart';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print(
    "\uD83D\uDCE8 \uBC31\uADF8\uB77C\uC6B4\uB4DC \uBA54\uC2DC\uC9C0 \uC218\uC2E0: \${message.messageId}",
  );
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

  SystemChrome.setEnabledSystemUIMode(
    SystemUiMode.manual,
    overlays: [SystemUiOverlay.top, SystemUiOverlay.bottom],
  );
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.black,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Colors.black,
      systemNavigationBarIconBrightness: Brightness.light,
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
    _setupFCM();
  }

  void _setupFCM() async {
    NotificationSettings settings =
        await _firebaseMessaging.requestPermission();

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        print(
          "\uD83D\uDCE5 \uD3EC\uADF9\uB77C\uC6B4\uB4DC \uBA54\uC2DC\uC9C0 \uC218\uC2E0: \${message.notification?.title}",
        );
      });

      final fcmToken = await _firebaseMessaging.getToken();
      if (fcmToken != null) {
        print("\uD83D\uDCF1 FCM \uD1A0\uD070: \$fcmToken");
      } else {
        print(
          "\u274C FCM \uD1A0\uD070\uC744 \uAC00\uC9C0\uC624\uC9C0 \uBABB\uD588\uC5B4\uC694.",
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true, // 상태바 영역까지 확장 허용
      backgroundColor: Colors.black, // 혹시 모를 배경색 처리
      body: Container(
        padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top),
        color: Colors.black,
        child: InAppWebView(
          initialUrlRequest: URLRequest(
            url: WebUri("https://smartgersang.onrender.com"),
          ),
          initialSettings: InAppWebViewSettings(
            transparentBackground: false,
            useHybridComposition: true,
          ),
        ),
      ),
    );
  }
}
