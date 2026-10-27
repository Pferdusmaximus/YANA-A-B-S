import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';

class ApiClient {
  Future<dynamic> get(String endpoint) async {
    final url = Uri.parse(
      '${ApiConfig.baseUrl}$endpoint',
    );

    final response = await http.get(url).timeout(
      const Duration(seconds: 10),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'API-Fehler: HTTP ${response.statusCode}',
      );
    }

    return jsonDecode(
      utf8.decode(response.bodyBytes),
    );
  }
}
