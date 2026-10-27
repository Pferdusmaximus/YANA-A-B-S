import '../../../core/network/api_client.dart';
import 'emergency_model.dart';

class EmergencyRepository {
  final ApiClient _apiClient;

  EmergencyRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  Future<List<EmergencyContact>> getEmergencyContacts() async {
    final data = await _apiClient.get('/notfallnummern');

    if (data is! List) {
      throw const FormatException(
        'Unerwartetes Antwortformat für Notfallnummern',
      );
    }

    return data.map((item) {
      return EmergencyContact.fromJson(
        Map<String, dynamic>.from(item as Map),
      );
    }).toList();
  }
}