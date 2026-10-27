import '../../../core/network/api_client.dart';
import 'help_model.dart';

class HelpRepository {
  final ApiClient _apiClient;

  HelpRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  Future<List<HelpFacility>> getHelpFacilities() async {
    final data = await _apiClient.get('/hilfestellen');

    if (data is! List) {
      throw const FormatException(
        'Unerwartetes Antwortformat der API',
      );
    }

    return data.map((item) {
      return HelpFacility.fromJson(
        Map<String, dynamic>.from(item as Map),
      );
    }).toList();
  }
}
