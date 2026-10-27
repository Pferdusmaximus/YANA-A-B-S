
import 'package:flutter_test/flutter_test.dart';
import 'package:yana/features/help/data/help_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('YANA API - Hilfestellen abrufen', () async {
    final repository = HelpRepository();

    final hilfestellen =
        await repository.getHelpFacilities();

    expect(hilfestellen, isNotEmpty);

    for (final hilfestelle in hilfestellen) {
      expect(hilfestelle.id, greaterThan(0));
      expect(hilfestelle.name, isNotEmpty);
      expect(hilfestelle.address, isNotEmpty);
    }

    print(
      'Erfolgreich ${hilfestellen.length} '
      'Hilfestellen von FastAPI geladen.',
    );

    for (final hilfestelle in hilfestellen) {
      print(
        '${hilfestelle.id}: ${hilfestelle.name}',
      );
    }
  });
}
