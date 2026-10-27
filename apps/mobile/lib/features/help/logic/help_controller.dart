import 'package:flutter/foundation.dart';

import '../data/help_model.dart';
import '../data/help_repository.dart';

class HelpController extends ChangeNotifier {
  final HelpRepository _repository;

  HelpController({HelpRepository? repository})
      : _repository = repository ?? HelpRepository();

  List<HelpFacility> _facilities = [];
  bool _isLoading = false;
  String? _errorMessage;

  // Öffentliche Eigenschaften für die Benutzeroberfläche
  List<HelpFacility> get facilities =>
      List.unmodifiable(_facilities);

  bool get isLoading => _isLoading;

  String? get errorMessage => _errorMessage;

  // Hilfestellen von FastAPI abrufen
  Future<void> loadFacilities() async {
    if (_isLoading) return;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _repository.getHelpFacilities();

      if (_disposed) return;

      _facilities = result;
    } catch (error) {
      if (_disposed) return;

      _errorMessage =
          'Hilfestellen konnten nicht geladen werden.';
    } finally {
      if (!_disposed) {
        _isLoading = false;
        notifyListeners();
      }
    }
  }

  bool _disposed = false;

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}