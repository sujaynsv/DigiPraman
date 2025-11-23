import 'dart:io';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import '../services/api_service.dart';

import './verification_review_page.dart';

class LoanVerificationPage extends StatefulWidget {
  final String loanRefNo;

  const LoanVerificationPage({Key? key, required this.loanRefNo})
      : super(key: key);

  @override
  State<LoanVerificationPage> createState() => _LoanVerificationPageState();
}

class _LoanVerificationPageState extends State<LoanVerificationPage> {
  bool _assetPhotosComplete = false;
  bool _documentsComplete = false;
  bool _canSubmit = false;
  bool _loading = true;
  bool _uploading = false;

  int _assetPhotosCount = 0;
  int _documentsCount = 0;

  Position? _currentPosition;
  String? _currentAddress;

  @override
  void initState() {
    super.initState();
    _loadVerificationStatus();
  }

  Future<void> _loadVerificationStatus() async {
    try {
      final status =
          await ApiService.getVerificationStatus(widget.loanRefNo);
      setState(() {
        _assetPhotosCount = status['asset_photos_count'] ?? 0;
        _documentsCount = status['documents_count'] ?? 0;
        _assetPhotosComplete = status['asset_photos_complete'] ?? false;
        _documentsComplete = status['documents_complete'] ?? false;
        _canSubmit = status['can_submit'] ?? false;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _loading = false;
      });
      _showError('Failed to load verification status');
    }
  }

  Future<void> _captureLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        _showError('Location services are disabled. Please enable them.');
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          _showError('Location permission denied');
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        _showError('Location permissions are permanently denied');
        return;
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      List<Placemark> placemarks = await placemarkFromCoordinates(
        position.latitude,
        position.longitude,
      );

      Placemark place = placemarks.first;
      String address =
          "${place.street}, ${place.locality}, ${place.postalCode}, ${place.country}";

      setState(() {
        _currentPosition = position;
        _currentAddress = address;
      });

      _showLocationDialog();
    } catch (e) {
      _showError('Failed to capture location: $e');
    }
  }

  void _showLocationDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('Location Captured'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Your current location:',
                style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            Text(
              _currentAddress ?? 'Unknown',
              style: const TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            Text(
              'Lat: ${_currentPosition?.latitude.toStringAsFixed(6)}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            Text(
              'Lon: ${_currentPosition?.longitude.toStringAsFixed(6)}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _currentPosition = null;
                _currentAddress = null;
              });
              Navigator.pop(ctx);
            },
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _takeAssetPhoto();
            },
            child: const Text('Take Photo'),
          ),
        ],
      ),
    );
  }

  Future<void> _takeAssetPhoto() async {
    if (_currentPosition == null) {
      _showError('Location not captured');
      return;
    }

    final ImagePicker picker = ImagePicker();
    final XFile? photo = await picker.pickImage(source: ImageSource.camera);

    if (photo != null) {
      setState(() {
        _uploading = true;
      });

      try {
        await ApiService.uploadEvidence(
          loanRefNo: widget.loanRefNo,
          evidenceType: 'asset_photo',
          requirementType: 'identification',
          file: File(photo.path),
          latitude: _currentPosition!.latitude,
          longitude: _currentPosition!.longitude,
          captureAddress: _currentAddress,
        );

        setState(() {
          _currentPosition = null;
          _currentAddress = null;
        });

        _showSuccess('Asset photo uploaded successfully');
        await _loadVerificationStatus();
      } catch (e) {
        _showError('Failed to upload photo');
      } finally {
        setState(() {
          _uploading = false;
        });
      }
    }
  }

  Future<void> _uploadDocument(String requirementType) async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['jpg', 'jpeg', 'png', 'pdf'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        _uploading = true;
      });

      try {
        await ApiService.uploadEvidence(
          loanRefNo: widget.loanRefNo,
          evidenceType: 'document',
          requirementType: requirementType,
          file: File(result.files.single.path!),
        );

        _showSuccess('Document uploaded successfully');
        await _loadVerificationStatus();
      } catch (e) {
        _showError('Failed to upload document');
      } finally {
        setState(() {
          _uploading = false;
        });
      }
    }
  }

  Future<void> _submitVerification() async {
    setState(() {
      _uploading = true;
    });

    try {
      await ApiService.submitVerification(widget.loanRefNo);
      _showSuccess('Verification submitted successfully');
      Navigator.pop(context);
    } catch (e) {
      _showError('Failed to submit verification');
    } finally {
      setState(() {
        _uploading = false;
      });
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: Column(
          children: [
            const Text('Loan Verification',
                style: TextStyle(fontSize: 18)),
            Text(
              widget.loanRefNo,
              style: const TextStyle(fontSize: 12, color: Colors.white70),
            ),
          ],
        ),
        backgroundColor: Colors.green,
        centerTitle: true,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: Column(
                children: [
                  Expanded(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Verification Requirements',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Level 1: Asset Photos
                          _buildRequirementCard(
                            icon: Icons.camera_alt,
                            title: 'Asset Photos',
                            description:
                                'Clear photos of the purchased asset from multiple angles',
                            required: true,
                            complete: _assetPhotosComplete,
                            count: _assetPhotosCount,
                            onTap: _captureLocation,
                            buttonText: 'Take Photo',
                            enabled: !_uploading,
                          ),

                          const SizedBox(height: 16),

                          // Level 2: Documents (disabled until level 1 complete)
                          _buildRequirementCard(
                            icon: Icons.description,
                            title: 'Documents',
                            description:
                                'Purchase receipts, registration documents, etc.',
                            required: true,
                            complete: _documentsComplete,
                            count: _documentsCount,
                            onTap: _assetPhotosComplete
                                ? () => _showDocumentOptions()
                                : null,
                            buttonText: 'Upload Document',
                            enabled:
                                _assetPhotosComplete && !_uploading,
                            locked: !_assetPhotosComplete,
                          ),

                          if (_assetPhotosComplete && _documentsComplete)
                            Container(
                              margin: const EdgeInsets.only(top: 16),
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.green.shade50,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                    color: Colors.green.shade200),
                              ),
                              child: Row(
                                children: const [
                                  Icon(Icons.check_circle,
                                      color: Colors.green),
                                  SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      'All requirements completed! You can now submit verification.',
                                      style: TextStyle(
                                          fontSize: 13,
                                          color: Colors.green),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),

                  // Submit button
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
                      onPressed: _canSubmit && !_uploading
                          ? () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) =>
                                      VerificationReviewPage(loanRefNo: widget.loanRefNo),
                                ),
                              );
                            }
                          : null,

                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          disabledBackgroundColor: Colors.grey.shade300,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              _uploading
                                  ? 'Processing...'
                                  : _canSubmit
                                      ? 'Submit Verification ($_assetPhotosCount + $_documentsCount items)'
                                      : 'Complete requirements to submit',
                              style: TextStyle(
                                fontSize: 16,
                                color: _canSubmit
                                    ? Colors.white
                                    : Colors.grey.shade600,
                              ),
                            ),
                            if (_canSubmit) ...[
                              const SizedBox(width: 8),
                              const Icon(Icons.arrow_forward,
                                  color: Colors.white),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildRequirementCard({
    required IconData icon,
    required String title,
    required String description,
    required bool required,
    required bool complete,
    required int count,
    required VoidCallback? onTap,
    required String buttonText,
    required bool enabled,
    bool locked = false,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: complete
              ? Colors.green.shade200
              : locked
                  ? Colors.grey.shade300
                  : Colors.orange.shade200,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: complete
                        ? Colors.green.shade100
                        : locked
                            ? Colors.grey.shade200
                            : Colors.orange.shade100,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    icon,
                    color: complete
                        ? Colors.green
                        : locked
                            ? Colors.grey
                            : Colors.orange,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            title,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(width: 8),
                          if (required)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.red.shade50,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Text(
                                'Required',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Colors.red,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                        ],
                      ),
                      if (count > 0)
                        Text(
                          '$count uploaded',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.green.shade700,
                          ),
                        ),
                    ],
                  ),
                ),
                if (complete)
                  const Icon(Icons.check_circle, color: Colors.green),
                if (locked)
                  const Icon(Icons.lock_outline, color: Colors.grey),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              description,
              style: const TextStyle(fontSize: 13, color: Colors.grey),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: enabled && onTap != null ? onTap : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  disabledBackgroundColor: Colors.grey.shade300,
                ),
                child: Text(
                  locked ? '🔒 Complete previous step' : buttonText,
                  style: TextStyle(
                    color: enabled ? Colors.white : Colors.grey.shade600,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showDocumentOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Select Document Type',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 16),
                ListTile(
                  leading:
                      const Icon(Icons.receipt_long, color: Colors.green),
                  title: const Text('Purchase Receipt'),
                  subtitle: const Text('Original bill/invoice'),
                  onTap: () {
                    Navigator.pop(ctx);
                    _uploadDocument('purchase_receipt');
                  },
                ),
                ListTile(
                  leading:
                      const Icon(Icons.description, color: Colors.green),
                  title: const Text('Registration Document'),
                  subtitle: const Text('Vehicle/equipment registration'),
                  onTap: () {
                    Navigator.pop(ctx);
                    _uploadDocument('registration');
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.folder, color: Colors.green),
                  title: const Text('Other Document'),
                  onTap: () {
                    Navigator.pop(ctx);
                    _uploadDocument('other');
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
