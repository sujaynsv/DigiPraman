import 'package:flutter/material.dart';
import 'api_service.dart';

class DatabaseTestPage extends StatefulWidget {
  @override
  _DatabaseTestPageState createState() => _DatabaseTestPageState();
}

class _DatabaseTestPageState extends State<DatabaseTestPage> {
  final ApiService _apiService = ApiService();
  final TextEditingController _nameController = TextEditingController();
  
  bool _isLoading = false;
  String _connectionStatus = 'Not tested';
  List<dynamic> _organizations = [];

  @override
  void initState() {
    super.initState();
    _testConnection();
  }

  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
      _connectionStatus = 'Testing...';
    });

    try {
      final result = await _apiService.testConnection();
      setState(() {
        _connectionStatus = '✅ Connected: ${result['message']}';
        _isLoading = false;
      });
      _loadOrganizations();
    } catch (e) {
      setState(() {
        _connectionStatus = '❌ Failed: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadOrganizations() async {
    setState(() => _isLoading = true);
    
    try {
      final orgs = await _apiService.getOrganizations();
      setState(() {
        _organizations = orgs;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Error loading: $e');
    }
  }

  Future<void> _createOrganization() async {
    if (_nameController.text.isEmpty) {
      _showError('Please enter organization name');
      return;
    }

    setState(() => _isLoading = true);

    try {
      await _apiService.createOrganization(
        _nameController.text,
        'financial',
      );
      
      _nameController.clear();
      _showSuccess('Organization created!');
      _loadOrganizations();
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Error: $e');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Database Connection Test'),
        backgroundColor: Colors.green,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Connection Status
            Card(
              color: _connectionStatus.contains('✅')
                  ? Colors.green.shade50
                  : Colors.orange.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      'Connection Status',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(_connectionStatus),
                    SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: _testConnection,
                      child: Text('Test Again'),
                    ),
                  ],
                ),
              ),
            ),

            SizedBox(height: 20),

            // Create Organization Form
            Text(
              'Create Organization',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            
            TextField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: 'Organization Name',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                hintText: 'e.g., Rural Bank',
              ),
            ),
            
            SizedBox(height: 10),
            
            ElevatedButton(
              onPressed: _isLoading ? null : _createOrganization,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                minimumSize: Size(double.infinity, 50),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isLoading
                  ? SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Text(
                      'Create Organization',
                      style: TextStyle(fontSize: 16, color: Colors.white),
                    ),
            ),

            SizedBox(height: 20),

            // Organizations List
            Text(
              'Organizations (${_organizations.length})',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            
            SizedBox(height: 10),
            
            Expanded(
              child: _isLoading
                  ? Center(child: CircularProgressIndicator())
                  : _organizations.isEmpty
                      ? Center(
                          child: Text(
                            'No organizations yet.\nCreate one above!',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.grey),
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: _loadOrganizations,
                          child: ListView.builder(
                            itemCount: _organizations.length,
                            itemBuilder: (context, index) {
                              final org = _organizations[index];
                              return Card(
                                margin: EdgeInsets.only(bottom: 8),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: Colors.green,
                                    child: Text(
                                      org['name'][0].toUpperCase(),
                                      style: TextStyle(color: Colors.white),
                                    ),
                                  ),
                                  title: Text(
                                    org['name'],
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Text('Type: ${org['type'] ?? 'N/A'}'),
                                  trailing: Text(
                                    'ID: ${org['id'].toString().substring(0, 8)}...',
                                    style: TextStyle(fontSize: 12),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }
}
