import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import './application_tracking_page.dart';

class VerificationReviewPage extends StatefulWidget {
  final String loanRefNo;

  const VerificationReviewPage({Key? key, required this.loanRefNo})
      : super(key: key);

  @override
  State<VerificationReviewPage> createState() => _VerificationReviewPageState();
}

class _VerificationReviewPageState extends State<VerificationReviewPage> {
  late Future<List<Map<String, dynamic>>> _evidenceFuture;
  bool _uploading = false;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _evidenceFuture = ApiService.listEvidenceFull(widget.loanRefNo);
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  Future<void> _submitVerification() async {
    setState(() => _uploading = true);

    try {
      // 1. Submit verification evidence
      await ApiService.submitVerification(widget.loanRefNo);

      // 2. Trigger VIDYA AI risk scoring
      final vidyaResult = await ApiService.runVidyaForLoanRef(widget.loanRefNo);

      final riskTier = vidyaResult['risk_tier'] ?? 'unknown';
      final riskScore = vidyaResult['final_risk_score']?.toString() ?? '-';

      _showSuccess(
        'Verification submitted.\nRisk tier: $riskTier (score $riskScore)',
      );

      Navigator.pop(context, vidyaResult);
    } catch (e) {
      _showError('Failed to submit verification or run risk checks: $e');
    } finally {
      setState(() => _uploading = false);
    }
  }

  Future<void> _submitFinal() async {
    setState(() => _submitting = true);
    try {
      // Submit verification first
      await ApiService.submitVerificationFinal(widget.loanRefNo);

      // Trigger VIDYA AI risk scoring
      final vidyaResult = await ApiService.runVidyaForLoanRef(widget.loanRefNo);

      final riskTier = vidyaResult['risk_tier'] ?? 'unknown';
      final riskScore = vidyaResult['final_risk_score']?.toString() ?? '-';

      if (!mounted) return;

      _showSuccess(
        'Submitted successfully!\nRisk tier: $riskTier (score $riskScore)',
      );

      // Navigate to tracking page after short delay
      await Future.delayed(const Duration(seconds: 2));
      
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => ApplicationTrackingPage(loanRefNo: widget.loanRefNo),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      _showError('Failed to submit: $e');
      setState(() => _submitting = false);
    }
  }

  void _showPreview(Map<String, dynamic> evidence) {
    final fileData = evidence['file_data'] as String?;
    final fileType = evidence['file_type'] as String;
    final fileName = evidence['file_name'] as String;

    if (fileData == null || !fileData.startsWith('data:')) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preview data not available')),
      );
      return;
    }

    // Extract base64 part
    final base64Data = fileData.split(',').last;
    final bytes = base64Decode(base64Data);

    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AppBar(
              title: Text(fileName, style: const TextStyle(fontSize: 14)),
              automaticallyImplyLeading: false,
              actions: [
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(ctx),
                ),
              ],
            ),
            Expanded(
              child: fileType.startsWith('image/')
                  ? Image.memory(bytes, fit: BoxFit.contain)
                  : Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.picture_as_pdf, size: 64),
                          const SizedBox(height: 16),
                          Text(fileName),
                          const SizedBox(height: 8),
                          const Text('PDF preview not available in app',
                              style: TextStyle(fontSize: 12)),
                        ],
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          children: [
            const Text('Review Submission', style: TextStyle(fontSize: 18)),
            Text(
              widget.loanRefNo,
              style: const TextStyle(fontSize: 12, color: Colors.white70),
            ),
          ],
        ),
        backgroundColor: Colors.green,
        centerTitle: true,
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _evidenceFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return const Center(child: Text('Failed to load submitted items'));
          }
          final items = snapshot.data ?? [];

          final assetPhotos = items
              .where((e) => e['evidence_type'] == 'asset_photo')
              .toList();
          final documents =
              items.where((e) => e['evidence_type'] == 'document').toList();

          return Column(
            children: [
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    const Text(
                      'Submitted items',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),

                    _sectionHeader(
                      title: 'Asset photos',
                      count: assetPhotos.length,
                    ),
                    if (assetPhotos.isEmpty)
                      const Padding(
                        padding: EdgeInsets.only(bottom: 12),
                        child: Text(
                          'No asset photos uploaded yet.',
                          style: TextStyle(fontSize: 13, color: Colors.grey),
                        ),
                      )
                    else
                      ...assetPhotos.map((e) => _buildEvidenceTile(e)),

                    const SizedBox(height: 16),

                    _sectionHeader(
                      title: 'Documents',
                      count: documents.length,
                    ),
                    if (documents.isEmpty)
                      const Padding(
                        padding: EdgeInsets.only(bottom: 12),
                        child: Text(
                          'No documents uploaded yet.',
                          style: TextStyle(fontSize: 13, color: Colors.grey),
                        ),
                      )
                    else
                      ...documents.map((e) => _buildEvidenceTile(e)),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 8,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _submitting ? null : _submitFinal,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      _submitting ? 'Submitting...' : 'Submit for verification',
                      style: const TextStyle(fontSize: 16, color: Colors.white),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _sectionHeader({required String title, required int count}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        Text(
          '$count item${count == 1 ? '' : 's'}',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildEvidenceTile(Map<String, dynamic> e) {
    final fileName = (e['file_name'] ?? '') as String;
    final fileType = (e['file_type'] ?? '') as String;
    final reqType = (e['requirement_type'] ?? '') as String;
    final address = (e['capture_address'] ?? '') as String;

    final isImage = fileType.startsWith('image/');
    final isPdf = fileType == 'application/pdf';

    IconData icon;
    if (isImage) {
      icon = Icons.photo;
    } else if (isPdf) {
      icon = Icons.picture_as_pdf;
    } else {
      icon = Icons.insert_drive_file;
    }

    return Card(
      margin: const EdgeInsets.only(top: 8),
      child: ListTile(
        leading: Icon(icon, color: Colors.green),
        title: Text(
          fileName,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (reqType.isNotEmpty)
              Text(
                'Type: $reqType',
                style: const TextStyle(fontSize: 12),
              ),
            if (address.isNotEmpty)
              Text(
                address,
                style: const TextStyle(fontSize: 11, color: Colors.grey),
              ),
          ],
        ),
        trailing: ElevatedButton(
          onPressed: () => _showPreview(e),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          ),
          child: const Text('Preview', style: TextStyle(fontSize: 12, color: Colors.white)),
        ),
      ),
    );
  }
}
