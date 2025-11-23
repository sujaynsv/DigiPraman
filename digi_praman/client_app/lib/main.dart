import 'package:flutter/material.dart';

// ✅ Make sure these files actually exist inside lib/
import 'database_test_page.dart';
import 'translation_service.dart';
import 'phone_verification.dart';
import 'screens/otp_login_page.dart';
import 'screens/loan_page.dart';


void main() {
  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  String selectedLanguage = "en"; // default language
  Map<String, String> uiText = {};

  final Map<String, String> languages = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "gu": "Gujarati",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "ur": "Urdu",
    "ne": "Nepali",
    "or": "Odia",
    "si": "Sinhala",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ar": "Arabic",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean"
  };

  List<String> baseStrings = [
    "Welcome to Digital Loan Verification",
    "Submit digital evidence for your loan verification easily and securely",
    "Capture verification photos",
    "GPS location tagging",
    "Works offline",
    "Quick verification process",
    "Get Started",
    "Continue as Guest"
  ];

  Future<void> loadTranslatedText() async {
    Map<String, String> translated = {};

    for (int i = 0; i < baseStrings.length; i++) {
      translated[baseStrings[i]] =
          await TranslationService.translateText(baseStrings[i], selectedLanguage);
    }

    setState(() {
      uiText = translated;
    });
  }

  @override
  void initState() {
    super.initState();
    loadTranslatedText(); // load initial translations
  }

  @override
  Widget build(BuildContext context) {
  return MaterialApp(
  debugShowCheckedModeBanner: false,
  routes: {
    '/': (context) => LandingPage(
          selectedLanguage: selectedLanguage,
          uiText: uiText,
          baseStrings: baseStrings,
          languages: languages,
          onLanguageChanged: (lang) async {
            selectedLanguage = lang;
            await loadTranslatedText();
          },
        ),
    '/otpLogin': (context) => OTPLoginPage(
          languageCode: selectedLanguage,  // <-- pass language here
        ),
    '/home': (context) => HomePage(),
    '/phoneVerification': (context) =>
        PhoneVerificationPage(languageCode: selectedLanguage),
    '/databaseTest': (context) => DatabaseTestPage(),
  },
  initialRoute: '/',
);

  }
}


class LandingPage extends StatelessWidget {
  final String selectedLanguage;
  final Map<String, String> uiText;
  final List<String> baseStrings;
  final Map<String, String> languages;
  final Function(String) onLanguageChanged;

  LandingPage({
    required this.selectedLanguage,
    required this.uiText,
    required this.baseStrings,
    required this.languages,
    required this.onLanguageChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: uiText.isEmpty
          ? Center(child: CircularProgressIndicator())
          : SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    SizedBox(height: 20),
                    Text(
                      uiText[baseStrings[0]]!,
                      textAlign: TextAlign.center,
                      style:
                          TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 10),
                    Text(
                      uiText[baseStrings[1]]!,
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.grey),
                    ),
                    SizedBox(height: 40),

                    // Features
                    feature(uiText[baseStrings[2]]!),
                    feature(uiText[baseStrings[3]]!),
                    feature(uiText[baseStrings[4]]!),
                    feature(uiText[baseStrings[5]]!),

                    SizedBox(height: 25),

                    // ✅ Language Dropdown
                    DropdownButtonFormField<String>(
                      value: selectedLanguage,
                      items: languages.entries
                          .map((e) => DropdownMenuItem<String>(
                                value: e.key,
                                child: Text(e.value),
                              ))
                          .toList(),
                      onChanged: (value) async {
                        onLanguageChanged(value!);
                      },
                      decoration: InputDecoration(
                        labelText: "Select Language",
                        border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                    ),

                    SizedBox(height: 30),

                    // ✅ Get Started → OTP Login
                    ElevatedButton(
                      onPressed: () {
                        Navigator.pushNamed(context, '/otpLogin');
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        minimumSize: Size(double.infinity, 50),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                      ),
                      child: Text(
                        uiText[baseStrings[6]]!,
                        style: TextStyle(fontSize: 18, color: Colors.white),
                      ),
                    ),

                    SizedBox(height: 15),

                    // ✅ Test Database Button
                    TextButton(
                      onPressed: () {
                        Navigator.pushNamed(context, '/databaseTest');
                      },
                      child: Text(
                        "Test Database Connection",
                        style: TextStyle(fontSize: 15, color: Colors.blue),
                      ),
                    ),

                    // ✅ Continue as Guest
                    TextButton(
                      onPressed: () {},
                      child: Text(
                        uiText[baseStrings[7]]!,
                        style: TextStyle(fontSize: 15),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget feature(String text) {
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      padding: EdgeInsets.all(16),
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(text, style: TextStyle(fontSize: 16)),
    );
  }
}

// ✅ Simple Home Page (kept as placeholder)
class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Home Page'),
      ),
      body: Center(
        child: Text('Welcome Home!'),
      ),
    );
  }
}