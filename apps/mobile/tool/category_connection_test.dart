// ignore_for_file: avoid_print

import 'package:yana/features/category/data/category_repository.dart';

Future<void> main() async {
  print('YANA Kategorien-Verbindungstest gestartet...');
  print('');

  try {
    final repository = CategoryRepository();
    final kategorien = await repository.getCategories();

    print('Verbindung zu FastAPI erfolgreich!');
    print('Anzahl Kategorien: ${kategorien.length}');
    print('');

    for (final kategorie in kategorien) {
      print('ID: ${kategorie.id}');
      print('Name: ${kategorie.name}');
      print('Beschreibung: ${kategorie.description ?? "Keine"}');
      print('-----------------------------');
    }

    if (kategorien.isEmpty) {
      print('Die API funktioniert, aber es sind keine Kategorien gespeichert.');
    } else {
      print('Kategorien erfolgreich aus PostgreSQL geladen!');
    }
  } catch (error) {
    print('FEHLER beim Abrufen der Kategorien:');
    print(error);
    rethrow;
  }
}
