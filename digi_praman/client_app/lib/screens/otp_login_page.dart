import 'package:flutter/material.dart';
import '../services/api_service.dart';

import './loan_page.dart';

class OTPLoginPage extends StatefulWidget {
  final String languageCode; // "en", "hi", etc.

  const OTPLoginPage({Key? key, required this.languageCode}) : super(key: key);

  @override
  State<OTPLoginPage> createState() => _OTPLoginPageState();
}

class _OTPLoginPageState extends State<OTPLoginPage> {
  final TextEditingController _mobileController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();

  bool _isLoading = false;
  bool _otpSent = false;

  String _selectedCountryCode = "+91";

  Future<void> _sendOtp() async {
    if (_mobileController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please enter mobile number')),
      );
      return;
    }
    setState(() => _isLoading = true);
    try {
      await ApiService.sendOtp("$_selectedCountryCode${_mobileController.text}");
      setState(() {
        _otpSent = true;
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('OTP sent successfully')),
      );
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send OTP: $e')),
      );
    }
  }

  Future<void> _verifyOtp() async {
    if (_otpController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please enter OTP')),
      );
      return;
    }
    setState(() => _isLoading = true);
    try {
      var result = await ApiService.verifyOtp(
        "$_selectedCountryCode${_mobileController.text}",
        _otpController.text,
      );
      setState(() => _isLoading = false);
      if (result['status'] == 'verified') {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => LoansPage(
              mobile: "$_selectedCountryCode${_mobileController.text}",
      languageCode: widget.languageCode,
            ),
          ),
        );
      }
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('OTP verification failed: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: true, // ✅ Allows UI to shift above keypad
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text('Login with OTP'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),

      /// ✅ Bottom button stays fixed
      bottomNavigationBar: Padding(
        padding: EdgeInsets.fromLTRB(20, 10, 20, 20),
        child: SizedBox(
          height: 52,
          child: ElevatedButton(
            onPressed: _isLoading
                ? null
                : _otpSent
                    ? _verifyOtp
                    : _sendOtp,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: _isLoading
                ? CircularProgressIndicator(color: Colors.white)
                : Text(
                    _otpSent ? 'Verify OTP' : 'Send OTP',
                    style: TextStyle(fontSize: 16, color: Colors.white),
                  ),
          ),
        ),
      ),

      /// ✅ Content scrolls, keypad stays at bottom
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(22.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 10),
            Text(
              "Welcome 👋",
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            SizedBox(height: 6),
            Text(
              "Enter your phone number to receive OTP",
              style: TextStyle(color: Colors.black54, fontSize: 14),
            ),
            SizedBox(height: 28),

            Row(
              children: [
                Container(
                  width: 110,
                  child: DropdownButtonFormField<String>(
                    value: _selectedCountryCode,
                    decoration: InputDecoration(
                      labelText: "Code",
                      filled: true,
                      fillColor: Colors.grey.shade100,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    items: [
                      "+91",
                      "+1",
                      "+44",
                      "+61",
                      "+971"
                    ].map((code) {
                      return DropdownMenuItem(
                        value: code,
                        child: Text(code),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedCountryCode = value!;
                      });
                    },
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _mobileController,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      labelText: "Phone Number",
                      filled: true,
                      fillColor: Colors.grey.shade100,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),

            if (_otpSent)
              Padding(
                padding: const EdgeInsets.only(top: 20),
                child: TextField(
                  controller: _otpController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: "Enter OTP",
                    filled: true,
                    fillColor: Colors.grey.shade100,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),

            SizedBox(height: 120), // ✅ Ensures keypad never overlaps fields
          ],
        ),
      ),
    );
  }
}