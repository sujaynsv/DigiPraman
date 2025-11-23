import 'package:flutter/material.dart';
import '../services/api_service.dart';

class VerificationReviewPage extends StatefulWidget {
  final String loanRefNo;

  const VerificationReviewPage({Key? key, required this.loanRefNo})
      : super(key: key);

  @override
  State<VerificationReviewPage> createState() => _VerificationReviewPageState();
}

class _VerificationReviewPageState extends State<VerificationReviewPage> {
  late Future<List<Map<String, dynamic>>> _evidenceFuture;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _evidenceFuture = ApiService.listEvidence(widget.loanRefNo);
  }

  Future<void> _submitFinal() async {
    setState(() => _submitting = true);
    try {
      await ApiService.submitVerification(widget.loanRefNo);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Verification submitted for review')),
      );
      Navigator.pop(context); // go back to loans page
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to submit. Please try again.')),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
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
                          style:
                              TextStyle(fontSize: 13, color: Colors.grey),
                        ),
                      )
                    else
                      ...assetPhotos.map(_buildEvidenceTile),

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
                          style:
                              TextStyle(fontSize: 13, color: Colors.grey),
                        ),
                      )
                    else
                      ...documents.map(_buildEvidenceTile),
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
                      padding:
                          const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      _submitting ? 'Submitting...' : 'Submit for verification',
                      style:
                          const TextStyle(fontSize: 16, color: Colors.white),
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
        onTap: () {
          // Placeholder: later we can open full-screen viewer by fetching the file
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text('Preview not implemented in prototype')),
          );
        },
      ),
    );
  }
}
