import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  
  // For iOS Simulator: use localhost
  // For Android Emulator: use 10.0.2.2
  // For physical device: use your computer's IP address
static const String baseUrl = 'http://192.168.0.5:8000';
  
  // Test connection
  Future<Map<String, dynamic>> testConnection() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/'));
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Connection failed: $e');
    }
  }

  // Create Organization
  Future<Map<String, dynamic>> createOrganization(
    String name,
    String? type,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/organizations/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          'type': type ?? 'test',
          'config': {},
        }),
      );

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to create: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  // Get Organizations
  Future<List<dynamic>> getOrganizations() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/organizations/'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load organizations');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }
}
