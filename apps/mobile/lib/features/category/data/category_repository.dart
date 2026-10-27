import '../../../core/network/api_client.dart';
import 'category_model.dart';

class CategoryRepository {
  final ApiClient _apiClient;

  CategoryRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  Future<List<YanaCategory>> getCategories() async {
    final data = await _apiClient.get('/kategorien');

    if (data is! List) {
      throw const FormatException(
        'Unerwartetes Antwortformat für Kategorien',
      );
    }

    return data.map((item) {
      return YanaCategory.fromJson(
        Map<String, dynamic>.from(item as Map),
      );
    }).toList();
  }
}