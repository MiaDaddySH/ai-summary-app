import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // static const String baseUrl = "http://10.0.2.2:8000"; // Android emulator
  static const String baseUrl = "http://127.0.0.1:8000"; // iOS simulator

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
      final data = jsonDecode(resp.body);
      return (data["summary"] ?? "").toString();
    }

    // 关键：把后端返回内容打印出来
    throw Exception("HTTP ${resp.statusCode}: ${resp.body}");
  }
}