import 'package:url_launcher/url_launcher.dart';

Future<void> callNumber(String number) async {
  final uri = Uri(scheme: 'tel', path: number);
  if (await canLaunchUrl(uri)) {
    await launchUrl(uri);
  }
}
