// ignore_for_file: avoid_print

import 'package:yana/features/emergency/data/emergency_repository.dart';

Future<void> main() async {
  print('YANA Notfallnummern-Verbindungstest gestartet...');
  print('');

  try {
    final repository = EmergencyRepository();

    final notfallnummern =
        await repository.getEmergencyContacts();

    print('Verbindung zu FastAPI erfolgreich!');
    print('Anzahl Notfallnummern: ${notfallnummern.length}');
    print('');

    for (final kontakt in notfallnummern) {
      print('ID: ${kontakt.id}');
      print('Name: ${kontakt.name}');
      print('Telefon: ${kontakt.phoneNumber}');
      print('Kategorie-ID: ${kontakt.categoryId ?? "Keine"}');
      print('Beschreibung: ${kontakt.description}');
      print('Erreichbarkeit: ${kontakt.availability}');
      print('-----------------------------');
    }

    if (notfallnummern.isEmpty) {
      print(
        'Verbindung erfolgreich, '
        'aber noch keine Notfallnummern vorhanden.',
      );
    } else {
      print(
        'Notfallnummern erfolgreich '
        'aus PostgreSQL geladen!',
      );
    }
  } catch (error) {
    print('FEHLER beim Abrufen der Notfallnummern:');
    print(error);
    rethrow;
  }
}