import 'package:flutter/foundation.dart';

import '../data/category_model.dart';
import '../data/category_repository.dart';

class CategoryController extends ChangeNotifier {
  final CategoryRepository _repository;

  CategoryController({CategoryRepository? repository})
      : _repository = repository ?? CategoryRepository();

  List<YanaCategory> _categories = [];
  bool _isLoading = false;
  bool _disposed = false;
  String? _errorMessage;

  // Eigenschaften für die Benutzeroberfläche
  List<YanaCategory> get categories =>
      List.unmodifiable(_categories);

  bool get isLoading => _isLoading;

  String? get errorMessage => _errorMessage;

  // Kategorien von FastAPI laden
  Future<void> loadCategories() async {
    if (_isLoading || _disposed) return;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _repository.getCategories();

      if (_disposed) return;

      _categories = result;
    } catch (error) {
      if (_disposed) return;

      _errorMessage =
          'Kategorien konnten nicht geladen werden.';
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