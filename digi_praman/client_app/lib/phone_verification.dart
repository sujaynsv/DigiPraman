import 'package:flutter/material.dart';
import 'translation_service.dart';

class PhoneVerificationPage extends StatefulWidget {
  final String languageCode;

  PhoneVerificationPage({required this.languageCode});

  @override
  _PhoneVerificationPageState createState() => _PhoneVerificationPageState();
}

class _PhoneVerificationPageState extends State<PhoneVerificationPage> {
  Map<String, String> uiText = {};

  List<String> baseStrings = [
    "Phone Verification",
    "Enter Your Mobile Number",
    "We will send you a verification code to confirm your identity",
    "Standard SMS charges may apply. We respect your privacy and will never share your number.",
    "Sending OTP..."
  ];

  Future<void> loadTranslated() async {
    Map<String, String> result = {};

    for (String text in baseStrings) {
      result[text] =
          await TranslationService.translateText(text, widget.languageCode);
    }

    setState(() {
      uiText = result;
    });
  }

  @override
  void initState() {
    super.initState();
    loadTranslated();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: uiText.isEmpty
          ? Center(child: CircularProgressIndicator())
          : SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    // Title
                    Text(
                      uiText[baseStrings[0]]!,
                      style:
                          TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 30),

                    // Description
                    Text(
                      uiText[baseStrings[1]]!,
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                    SizedBox(height: 10),
                    Text(
                      uiText[baseStrings[2]]!,
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.grey),
                    ),

                    SizedBox(height: 30),

                    // Phone input
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(14),
                          border:
                              Border.all(color: Colors.black12, width: 1.2)),
                      child: Row(
                        children: [
                          Text("+91",
                              style: TextStyle(
                                  fontSize: 18, fontWeight: FontWeight.bold)),
                          SizedBox(width: 12),
                          Expanded(
                            child: TextField(
                              keyboardType: TextInputType.number,
                              decoration: InputDecoration(
                                  border: InputBorder.none,
                                  hintText: "7386545459"),
                            ),
                          )
                        ],
                      ),
                    ),

                    SizedBox(height: 15),

                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.warning, color: Colors.orange),
                          SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              uiText[baseStrings[3]]!,
                              style: TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),

                    Spacer(),

                    ElevatedButton(
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.grey,
                          minimumSize: Size(double.infinity, 50),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14))),
                      child: Text(
                        uiText[baseStrings[4]]!,
                        style: TextStyle(color: Colors.white),
                      ),
                    ),

                    SizedBox(height: 20),
                  ],
                ),
              ),
            ),
    );
  }
}