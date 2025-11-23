import 'package:flutter/material.dart';

class VerificationPlaceholderPage extends StatelessWidget {
  final String loanRefNo;

  const VerificationPlaceholderPage({Key? key, required this.loanRefNo})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Verification (Coming Soon)'),
        backgroundColor: Colors.green,
      ),
      body: Center(
        child: Text(
          'Placeholder for verification flow.\nLoan: $loanRefNo',
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 16),
        ),
      ),
    );
  }
}
