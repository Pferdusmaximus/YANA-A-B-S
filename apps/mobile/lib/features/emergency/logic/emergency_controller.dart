import 'package:flutter/foundation.dart';

import '../data/emergency_model.dart';
import '../data/emergency_repository.dart';

class EmergencyController extends ChangeNotifier {
  final EmergencyRepository _repository;

  EmergencyController({EmergencyRepository? repository})
      : _repository = repository ?? EmergencyRepository();

  List<EmergencyContact> _contacts = [];
  bool _isLoading = false;
  bool _disposed = false;
  String? _errorMessage;

  List<EmergencyContact> get contacts =>
      List.unmodifiable(_contacts);

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> loadContacts() async {
    if (_isLoading || _disposed) return;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _repository.getEmergencyContacts();

      if (_disposed) return;

      _contacts = result;
    } catch (error) {
      if (_disposed) return;

      _errorMessage =
          'Notfallnummern konnten nicht geladen werden.';
    } finally {
      if (!_disposed) {
        _isLoading = false;
        notifyListeners();
      }
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
