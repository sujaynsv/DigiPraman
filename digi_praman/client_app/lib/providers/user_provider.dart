import 'package:flutter/material.dart';

class UserProvider extends ChangeNotifier {
  String? id;
  String? mobile;
  String? name;

  bool get loggedIn => id != null;

  void setUser(Map u) {
    id = u['id'];
    mobile = u['mobile'];
    name = u['name'];
    notifyListeners();
  }
}
