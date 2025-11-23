import 'package:flutter/material.dart';
import '../services/api_service.dart';
import './verification_placeholder_page.dart';

class UserProfilePage extends StatefulWidget {
  final String mobile;
  final String userName;
  final List<Map<String, dynamic>> loans;

  const UserProfilePage({
    Key? key,
    required this.mobile,
    required this.userName,
    required this.loans,
  }) : super(key: key);

  @override
  State<UserProfilePage> createState() => _UserProfilePageState();
}

class _UserProfilePageState extends State<UserProfilePage> {
  late TextEditingController _nameController;
  late TextEditingController _emailController;
  late TextEditingController _statusController;
  late TextEditingController _mobileController;

  String? _userId;
  bool _loading = true;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.userName);
    _emailController = TextEditingController();
    _statusController = TextEditingController();
    _mobileController = TextEditingController(text: widget.mobile);
    _loadUserFromBackend();
  }

  Future<void> _loadUserFromBackend() async {
    try {
      final userJson = await ApiService.fetchUserByMobile(widget.mobile);
      setState(() {
        _userId = userJson['id'] as String?;
        _nameController.text = (userJson['name'] ?? widget.userName).toString();
        _emailController.text = (userJson['email'] ?? '').toString();
        _statusController.text = (userJson['status'] ?? 'active').toString();
        _mobileController.text = (userJson['mobile'] ?? widget.mobile).toString();
        _loading = false;
        _error = null;
      });
    } catch (e) {
      setState(() {
        _loading = false;
        _error = 'Failed to load profile';
      });
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _statusController.dispose();
    _mobileController.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    if (_userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('User not found in backend')),
      );
      return;
    }

    setState(() {
      _saving = true;
    });

    try {
      final body = <String, dynamic>{
        'name': _nameController.text.trim(),
        'email': _emailController.text.trim().isEmpty
            ? null
            : _emailController.text.trim(),
        'status': _statusController.text.trim().isEmpty
            ? null
            : _statusController.text.trim(),
        // mobile is intentionally not sent (cannot be edited)
      };

      body.removeWhere((key, value) => value == null);

      final updatedUser = await ApiService.updateUser(_userId!, body);

      setState(() {
        _nameController.text = (updatedUser['name'] ?? '').toString();
        _emailController.text = (updatedUser['email'] ?? '').toString();
        _statusController.text = (updatedUser['status'] ?? '').toString();
        _saving = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile updated successfully')),
      );

      // Return updated name to LoansPage
      Navigator.pop(context, _nameController.text.trim());
    } catch (e) {
      setState(() {
        _saving = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to save profile changes')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final initials = _nameController.text.isNotEmpty
        ? _nameController.text
            .trim()
            .split(' ')
            .map((e) => e[0])
            .take(2)
            .join()
            .toUpperCase()
        : 'U';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Profile'),
        backgroundColor: Colors.green,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : SafeArea(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 32,
                              backgroundColor: Colors.green.shade100,
                              child: Text(
                                initials,
                                style: const TextStyle(
                                  color: Colors.green,
                                  fontSize: 22,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _nameController.text,
                                  style: const TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  _mobileController.text,
                                  style: const TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),

                        const Text(
                          'Profile details',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 12),

                        TextField(
                          controller: _nameController,
                          decoration: const InputDecoration(
                            labelText: 'Full name',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 12),

                        TextField(
                          controller: _mobileController,
                          enabled: false,
                          decoration: const InputDecoration(
                            labelText: 'Mobile number',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 12),

                        TextField(
                          controller: _emailController,
                          decoration: const InputDecoration(
                            labelText: 'Email (optional)',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 12),

                        TextField(
                          controller: _statusController,
                          decoration: const InputDecoration(
                            labelText: 'Status',
                            helperText: 'e.g. active, inactive',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 16),

                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: _saving ? null : _saveProfile,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                            ),
                            child: Text(_saving ? 'Saving...' : 'Save changes'),
                          ),
                        ),

                        const SizedBox(height: 24),
                        const Text(
                          'Your loan applications',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 8),

                        if (widget.loans.isEmpty)
                          const Padding(
                            padding: EdgeInsets.symmetric(vertical: 16),
                            child: Text('No loans linked to this profile.'),
                          )
                        else
                          ListView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: widget.loans.length,
                            itemBuilder: (context, index) {
                              final loan = widget.loans[index];
                              final ref = loan['loan_ref_no'] ?? '';
                              final purpose = loan['purpose'] ?? '';
                              final status =
                                  (loan['lifecycle_status'] ?? '').toString();
                              final double? amount =
                                  loan['sanctioned_amount'] is num
                                      ? (loan['sanctioned_amount'] as num)
                                          .toDouble()
                                      : null;

                              return Card(
                                margin: const EdgeInsets.only(bottom: 12),
                                child: ListTile(
                                  title: Text(ref),
                                  subtitle: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(purpose),
                                      if (amount != null)
                                        Text(
                                            'Amount: ₹${amount.toStringAsFixed(0)}'),
                                    ],
                                  ),
                                  trailing: Text(
                                    status.isEmpty ? 'Active' : status,
                                    style: const TextStyle(fontSize: 12),
                                  ),
                                  onTap: () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (_) =>
                                            VerificationPlaceholderPage(
                                          loanRefNo: ref,
                                        ),
                                      ),
                                    );
                                  },
                                ),
                              );
                            },
                          ),
                      ],
                    ),
                  ),
                ),
    );
  }
}
