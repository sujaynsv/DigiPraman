import 'dart:convert';
import 'package:http/http.dart' as http;

class TranslationService {
  static const String apiKey = "AIzaSyBqftvYMg5-RSaPMtxM-DZPLH18o_CoNPg";

  static Future<String> translateText(String text, String targetLang) async {
    final url =
        "https://translation.googleapis.com/language/translate/v2?key=$apiKey";

    final response = await http.post(
      Uri.parse(url),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "q": text,
        "target": targetLang,
        "format": "text",
      }),
    );

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body);
      return body["data"]["translations"][0]["translatedText"];
    } else {
      return text; // fallback
    }
  }
}