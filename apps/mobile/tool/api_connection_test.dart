// ignore_for_file: avoid_print

import 'package:yana/features/help/data/help_repository.dart';

Future<void> main() async {
  print('YANA API-Verbindungstest gestartet...');
  print('');

  try {
    final repository = HelpRepository();

    final hilfestellen =
        await repository.getHelpFacilities();

    print('Verbindung zu FastAPI erfolgreich!');
    print('Anzahl Hilfestellen: ${hilfestellen.length}');
    print('');

    for (final hilfestelle in hilfestellen) {
      print('ID: ${hilfestelle.id}');
      print('Name: ${hilfestelle.name}');
      print('Typ: ${hilfestelle.type}');
      print('Adresse: ${hilfestelle.address}');
      print('-----------------------------');
    }

    if (hilfestellen.isEmpty) {
      print('Verbindung erfolgreich, aber keine Daten vorhanden.');
    } else {
      print('YANA API-Verbindungstest erfolgreich abgeschlossen!');
    }
  } catch (error) {
    print('FEHLER beim API-Verbindungstest:');
    print(error);
    rethrow;
  }
}
