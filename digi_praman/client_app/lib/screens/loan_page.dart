import 'dart:typed_data';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import './loan_verification_page.dart';
import '../services/api_service.dart';
import './verification_placeholder_page.dart';
import './user_profile_page.dart';
import './application_tracking_page.dart';
import './video_call_page.dart';



class LoansPage extends StatefulWidget {
  final String mobile;
  final String languageCode;

  const LoansPage({
    Key? key,
    required this.mobile,
    required this.languageCode,
  }) : super(key: key);

  @override
  State<LoansPage> createState() => _LoansPageState();
}

class _LoansPageState extends State<LoansPage> {
  late Future<Map<String, dynamic>> _summaryFuture;
  final AudioPlayer _audioPlayer = AudioPlayer();
  late String _languageCode;
  String? _overrideUserName;
  int _selectedTab = 0; // 0 = pending, 1 = submitted

  @override
  void initState() {
    super.initState();
    _summaryFuture = ApiService.fetchLoanSummary(widget.mobile);
    _languageCode = _mapUiLangToTts(widget.languageCode);
  }

  String _mapUiLangToTts(String uiLang) {
    switch (uiLang) {
      case 'hi':
        return 'hi-IN';
      case 'te':
        return 'te-IN';
      case 'ta':
        return 'ta-IN';
      case 'bn':
        return 'bn-IN';
      default:
        return 'en-IN';
    }
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _speakPageSummary(Map<String, dynamic> summary) async {
    final userName = summary['user_name'] ?? 'user';
    final active = summary['active_loans_count'] ?? 0;
    final pending = summary['pending_verification_count'] ?? 0;

    final text =
        'Hi $userName. You have $active active loans, and $pending loans pending verification. '
        'Tap on a loan card to view details or submit verification documents.';

    try {
      final Uint8List audioBytes =
          await ApiService.fetchTtsAudio(text: text, languageCode: _languageCode);

      final dir = await getTemporaryDirectory();
      final filePath =
          '${dir.path}/tts_${DateTime.now().millisecondsSinceEpoch}.mp3';
      final file = File(filePath);
      await file.writeAsBytes(audioBytes, flush: true);

      await _audioPlayer.stop();
      await _audioPlayer.play(DeviceFileSource(filePath));
    } catch (e) {
      debugPrint('TTS play error: $e');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to play audio right now')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: FutureBuilder<Map<String, dynamic>>(
        future: _summaryFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || !snapshot.hasData) {
            return const Center(child: Text('Failed to load loans'));
          }

          final data = snapshot.data!;
          final userName =
              _overrideUserName ?? (data['user_name'] ?? 'User').toString();
          final active = data['active_loans_count'] ?? 0;
          final pending = data['pending_verification_count'] ?? 0;
          final loans = (data['loans'] as List<dynamic>?) ?? [];

          for (var loan in loans) {
            print('LOAN DEBUG: ref=${loan['loan_ref_no']}, stage=${loan['verification_stage']}, stage_type=${loan['verification_stage'].runtimeType}');
          }

          // Filter loans based on selected tab
// Filter loans based on selected tab
          final filteredLoans = loans.where((loan) {
            // Get the verification_stage as a string directly (backend sends it as string value)
            final stage = (loan['verification_stage'] as String?) ?? 'not_started';
            
            if (_selectedTab == 0) {
              // Pending verification tab - show loans NOT yet submitted
              return stage == 'not_started' ||
                  stage == 'documents_uploaded';
            } else {
              // Submitted tab - show loans that ARE submitted
              return stage == 'submitted' ||
                  stage == 'under_review' ||
                  stage == 'approved' ||
                  stage == 'rejected' ||
                  stage == 'video_verification_requested' ||
                  stage == 'video_verification_completed';
            }
          }).toList();


          return SafeArea(
            child: Column(
              children: [
                _buildHeader(userName, active, pending, data),
                
                // Tab bar
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      _buildTab('Pending Verification', 0),
                      const SizedBox(width: 4),
                      _buildTab('Submitted', 1),
                    ],
                  ),
                ),

                if (pending > 0 && _selectedTab == 0) _buildWarningBanner(),
                
                Expanded(
                  child: filteredLoans.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                _selectedTab == 0 
                                    ? Icons.assignment_outlined 
                                    : Icons.check_circle_outline,
                                size: 64,
                                color: Colors.grey,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                _selectedTab == 0
                                    ? 'No pending verifications'
                                    : 'No submitted applications',
                                style: const TextStyle(
                                  fontSize: 16,
                                  color: Colors.grey,
                                ),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: filteredLoans.length,
                          itemBuilder: (context, index) {
                            final loan =
                                filteredLoans[index] as Map<String, dynamic>;
                            return _buildLoanCard(loan);
                          },
                        ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildTab(String label, int index) {
    final isSelected = _selectedTab == index;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            _selectedTab = index;
          });
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? Colors.green : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.grey,
              fontSize: 13,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(
    String userName,
    int active,
    int pending,
    Map<String, dynamic> summary,
  ) {
    final initials = userName.isNotEmpty
        ? userName
            .trim()
            .split(' ')
            .map((e) => e[0])
            .take(2)
            .join()
            .toUpperCase()
        : 'U';

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
      decoration: const BoxDecoration(
        color: Colors.green,
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(16),
          bottomRight: Radius.circular(16),
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    radius: 22,
                    backgroundColor: Colors.white24,
                    child: Text(
                      initials,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Hello',
                        style: TextStyle(color: Colors.white70, fontSize: 12),
                      ),
                      Text(
                        userName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.mic, color: Colors.white),
                    onPressed: () => _speakPageSummary(summary),
                  ),
                  IconButton(
                    icon: const Icon(Icons.notifications, color: Colors.white),
                    onPressed: () => _showNotificationsSheet(context, summary),
                  ),
                  IconButton(
                    icon: const Icon(Icons.person, color: Colors.white),
                    onPressed: () async {
                      final loans = (summary['loans'] as List<dynamic>? ?? [])
                          .cast<Map<String, dynamic>>();

                      final updatedName = await Navigator.push<String>(
                        context,
                        MaterialPageRoute(
                          builder: (_) => UserProfilePage(
                            mobile: widget.mobile,
                            userName: userName,
                            loans: loans,
                          ),
                        ),
                      );

                      if (updatedName != null && updatedName.isNotEmpty) {
                        setState(() {
                          _overrideUserName = updatedName;
                          _summaryFuture =
                              ApiService.fetchLoanSummary(widget.mobile);
                        });
                      }
                    },
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _summaryCard(active.toString(), 'Active Loans'),
              _summaryCard(pending.toString(), 'Pending Verification'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _summaryCard(String value, String label) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Text(
              value,
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.green,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWarningBanner() {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Icon(Icons.warning_amber_rounded, color: Colors.red),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              'You have loans requiring verification. Please submit evidence before the deadline.',
              style: TextStyle(fontSize: 13, color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

Widget _buildLoanCard(Map<String, dynamic> loan) {
  final String ref = loan['loan_ref_no'] ?? '';
  final String purpose = loan['purpose'] ?? '';
  final String lifecycleStatus = (loan['lifecycle_status'] ?? '').toString();
  final String verificationStage = (loan['verification_stage'] as String?) ?? 'not_started';
  final double? amount = loan['sanctioned_amount'] is num
      ? (loan['sanctioned_amount'] as num).toDouble()
      : null;
  final String nextEmi = loan['next_emi_date'] ?? '';

  String statusLabel;
  Color statusColor;
  
  if (verificationStage == 'video_verification_requested') {
    statusLabel = 'Video Call Required';
    statusColor = Colors.blue;
  } else if (verificationStage == 'submitted' || verificationStage == 'under_review') {
    statusLabel = 'Submitted';
    statusColor = Colors.green;
  } else if (verificationStage == 'approved') {
    statusLabel = 'Approved';
    statusColor = Colors.green;
  } else if (verificationStage == 'rejected') {
    statusLabel = 'Rejected';
    statusColor = Colors.red;
  } else if (verificationStage == 'video_verification_completed') {
    statusLabel = 'Call Completed';
    statusColor = Colors.purple;
  } else if (lifecycleStatus == 'verification_required') {
    statusLabel = 'Verification Required';
    statusColor = Colors.red;
  } else if (lifecycleStatus == 'verification_pending') {
    statusLabel = 'Verification Pending';
    statusColor = Colors.orange;
  } else {
    statusLabel = lifecycleStatus.isEmpty ? 'Active' : lifecycleStatus;
    statusColor = Colors.green;
  }

  final bool isVideoCallRequired = verificationStage == 'video_verification_requested';
  
  final bool isSubmitted = verificationStage == 'submitted' ||
      verificationStage == 'under_review' ||
      verificationStage == 'approved' ||
      verificationStage == 'rejected' ||
      verificationStage == 'video_verification_requested' ||
      verificationStage == 'video_verification_completed';

  return Card(
    margin: const EdgeInsets.only(bottom: 16),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
      side: BorderSide(color: statusColor.withOpacity(0.4)),
    ),
    elevation: 2,
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                ref,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  statusLabel,
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            purpose,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _infoColumn(
                'Loan Amount',
                amount != null ? '₹${amount.toStringAsFixed(0)}' : '-',
              ),
              _infoColumn('Next EMI', nextEmi.isNotEmpty ? nextEmi : '-'),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
                        onPressed: () async {
            if (isVideoCallRequired) {
              // Go to video call page
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => VideoCallPage(
                    loanRefNo: ref,
                  ),
                ),
              );
              // Refresh on return
              setState(() {
                _summaryFuture = ApiService.fetchLoanSummary(widget.mobile);
              });
            } else if (isSubmitted) {
              // Go to tracking page
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ApplicationTrackingPage(
                    loanRefNo: ref,
                  ),
                ),
              );
              setState(() {
                _summaryFuture = ApiService.fetchLoanSummary(widget.mobile);
              });
            } else {
              // Go to verification page
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => LoanVerificationPage(
                    loanRefNo: ref,
                  ),
                ),
              );
              setState(() {
                _summaryFuture = ApiService.fetchLoanSummary(widget.mobile);
              });
            }
          },

              style: ElevatedButton.styleFrom(
                backgroundColor: isVideoCallRequired
                    ? Colors.blue
                    : (isSubmitted ? Colors.blue : Colors.green),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isVideoCallRequired
                        ? Icons.videocam
                        : (isSubmitted ? Icons.track_changes : Icons.upload_file),
                    size: 18,
                    color: Colors.white,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    isVideoCallRequired
                        ? 'Start Video Verification'
                        : (isSubmitted
                            ? 'View Application Status'
                            : 'Submit verification documents'),
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    ),
  );
}

  Widget _infoColumn(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label,
            style: const TextStyle(fontSize: 12, color: Colors.grey)),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  void _showNotificationsSheet(
    BuildContext context,
    Map<String, dynamic> summary,
  ) {
    final loans = (summary['loans'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();

    final pendingLoans = loans.where((loan) {
      final status = (loan['lifecycle_status'] ?? '').toString();
      return status == 'verification_required' ||
          status == 'verification_pending';
    }).toList();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        if (pendingLoans.isEmpty) {
          return Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: const [
                SizedBox(height: 8),
                Icon(Icons.notifications_none, size: 32, color: Colors.grey),
                SizedBox(height: 8),
                Text(
                  'No pending verifications',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                SizedBox(height: 12),
              ],
            ),
          );
        }

        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade400,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Pending Verifications',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Flexible(
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: pendingLoans.length,
                    itemBuilder: (context, index) {
                      final loan = pendingLoans[index];
                      final ref = loan['loan_ref_no'] ?? '';
                      final purpose = loan['purpose'] ?? '';
                      final status =
                          (loan['lifecycle_status'] ?? '').toString();

                      String statusLabel;
                      Color statusColor;
                      if (status == 'verification_required') {
                        statusLabel = 'Verification Required';
                        statusColor = Colors.red;
                      } else {
                        statusLabel = 'Verification Pending';
                        statusColor = Colors.orange;
                      }

                      return ListTile(
                        contentPadding:
                            const EdgeInsets.symmetric(vertical: 4),
                        title: Text(
                          ref,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        subtitle: Text(purpose),
                        trailing: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: statusColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            statusLabel,
                            style: TextStyle(
                              color: statusColor,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        onTap: () {
                          Navigator.pop(context);
                          Navigator.push(
                            this.context,
                            MaterialPageRoute(
                              builder: (_) => LoanVerificationPage(
                                loanRefNo: ref,
                              ),
                            ),
                          );
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
