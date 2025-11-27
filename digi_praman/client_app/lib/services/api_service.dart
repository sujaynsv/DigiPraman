import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:typed_data';
import 'dart:io';

class ApiService {
  
  // For iOS Simulator: use localhost
  // For Android Emulator: use 10.0.2.2
  // For physical device: use your computer's IP address
static const String baseUrl = 'https://7657ebfd7826.ngrok-free.app';

  
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
    static Future<void> sendOtp(String mobile) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/send-otp'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'mobile': mobile}),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to send OTP');
    }
  }

    static Future<Map<String, dynamic>> verifyOtp(String mobile, String otp) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/verify-otp'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'mobile': mobile,
        'otp': otp,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('OTP verification failed');
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

    static Future<List<dynamic>> fetchLoans(String mobile) async {
    final uri = Uri.parse('$baseUrl/loans').replace(queryParameters: {
      'mobile': mobile,
      'skip': '0',
      'limit': '20',
    });

    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as List<dynamic>;
    } else {
      throw Exception('Failed to load loans: ${response.body}');
    }
  }

    static Future<Map<String, dynamic>> fetchLoanSummary(String mobile) async {
    final uri = Uri.parse('$baseUrl/loans/summary').replace(queryParameters: {
      'mobile': mobile,
      'skip': '0',
      'limit': '20',
    });

    final response = await http.get(uri);
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to load loan summary: ${response.body}');
    }
  }

  static Future<Uint8List> fetchTtsAudio(
      {required String text, required String languageCode}) async {
    final uri = Uri.parse('$baseUrl/tts').replace(queryParameters: {
      'text': text,
      'language_code': languageCode,
    });

    final response = await http.post(uri);
    if (response.statusCode == 200) {
      return response.bodyBytes; // MP3 bytes
    } else {
      throw Exception('TTS failed: ${response.body}');
    }
  }
    static Future<Map<String, dynamic>> fetchUserByMobile(String mobile) async {
    final uri = Uri.parse('$baseUrl/users/mobile/$mobile');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to load user: ${response.body}');
    }
  }

  static Future<Map<String, dynamic>> updateUser(
      String userId, Map<String, dynamic> updateBody) async {
    final uri = Uri.parse('$baseUrl/users/$userId');
    final response = await http.patch(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(updateBody),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to update user: ${response.body}');
    }
  }

    static Future<Map<String, dynamic>> getVerificationStatus(
      String loanRefNo) async {
    final uri = Uri.parse('$baseUrl/loans/$loanRefNo/verification/status');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to get verification status');
    }
  }

  static Future<void> uploadEvidence({
    required String loanRefNo,
    required String evidenceType,
    required String requirementType,
    required File file,
    double? latitude,
    double? longitude,
    String? captureAddress,
  }) async {
    final uri = Uri.parse('$baseUrl/loans/$loanRefNo/evidence/upload');

    var request = http.MultipartRequest('POST', uri);
    request.fields['evidence_type'] = evidenceType;
    request.fields['requirement_type'] = requirementType;
    
    if (latitude != null) request.fields['latitude'] = latitude.toString();
    if (longitude != null) request.fields['longitude'] = longitude.toString();
    if (captureAddress != null) request.fields['capture_address'] = captureAddress;

    request.files.add(await http.MultipartFile.fromPath('file', file.path));

    var response = await request.send();

    if (response.statusCode != 200) {
      throw Exception('Failed to upload evidence');
    }
  }

  static Future<void> submitVerification(String loanRefNo) async {
    final uri = Uri.parse('$baseUrl/loans/$loanRefNo/verification/submit');
    final response = await http.post(uri);

    if (response.statusCode != 200) {
      throw Exception('Failed to submit verification');
    }
  }


  static Future<List<Map<String, dynamic>>> listEvidence(String loanRefNo) async {
  final uri = Uri.parse('$baseUrl/loans/$loanRefNo/evidence');
  final response = await http.get(uri);

  if (response.statusCode == 200) {
    final decoded = jsonDecode(response.body);
    if (decoded is List) {
      return decoded.cast<Map<String, dynamic>>();
    }
    throw Exception('Unexpected evidence payload');
  } else {
    throw Exception('Failed to load evidence');
  }
}
// Get evidence with full preview data
static Future<List<Map<String, dynamic>>> listEvidenceFull(String loanRefNo) async {
  final uri = Uri.parse('$baseUrl/loans/$loanRefNo/evidence/full');
  final response = await http.get(uri);

  if (response.statusCode == 200) {
    final decoded = jsonDecode(response.body);
    if (decoded is List) {
      return decoded.cast<Map<String, dynamic>>();
    }
    throw Exception('Unexpected evidence payload');
  } else {
    throw Exception('Failed to load evidence');
  }
}

// Get single evidence preview
static Future<Map<String, dynamic>> getEvidencePreview(
    String loanRefNo, String evidenceId) async {
  final uri = Uri.parse('$baseUrl/loans/$loanRefNo/evidence/$evidenceId/preview');
  final response = await http.get(uri);

  if (response.statusCode == 200) {
    return jsonDecode(response.body) as Map<String, dynamic>;
  } else {
    throw Exception('Failed to load preview');
  }
}

// Final submission
static Future<void> submitVerificationFinal(String loanRefNo) async {
  final uri = Uri.parse('$baseUrl/loans/$loanRefNo/verification/submit-final');
  final response = await http.post(uri);

  if (response.statusCode != 200) {
    throw Exception('Failed to submit verification');
  }
}

// Get application tracking
static Future<Map<String, dynamic>> getApplicationTracking(String loanRefNo) async {
  final uri = Uri.parse('$baseUrl/loans/$loanRefNo/tracking');
  final response = await http.get(uri);

  if (response.statusCode == 200) {
    return jsonDecode(response.body) as Map<String, dynamic>;
  } else {
    throw Exception('Failed to load tracking');
  }
}

static Future<Map<String, dynamic>> startVideoCall(String loanRefNo) async {
  final encodedRef = Uri.encodeComponent(loanRefNo);
  final uri = Uri.parse('$baseUrl/video-call/start/$encodedRef');
  
  final response = await http.post(uri);
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body) as Map<String, dynamic>;
  } else {
    throw Exception('Failed to start video call');
  }
}






}