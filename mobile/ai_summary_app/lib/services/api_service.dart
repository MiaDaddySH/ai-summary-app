import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    "API_BASE_URL",
    defaultValue: "http://127.0.0.1:8000",
  );

  static Future<String> summarize(String input) async {
    final uri = Uri.parse("$baseUrl/summarize");

    final trimmed = input.trim();
    final body = trimmed.startsWith("http://") || trimmed.startsWith("https://")
        ? {"url": trimmed}
        : {"text": trimmed};

    final resp = await http.post(
      uri,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    );

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      return (data["summary"] ?? "").toString();
    }

    throw Exception("HTTP ${resp.statusCode}: ${_extractErrorMessage(resp.body)}");
  }

  static String _extractErrorMessage(String responseBody) {
    try {
      final data = jsonDecode(responseBody);
      if (data is Map<String, dynamic>) {
        final detail = data["detail"];
        if (detail is String && detail.isNotEmpty) {
          return detail;
        }
      }
    } catch (_) {}
    return responseBody;
  }
}
