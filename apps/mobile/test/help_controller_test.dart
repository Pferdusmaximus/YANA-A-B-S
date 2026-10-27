import 'package:flutter_test/flutter_test.dart';

import 'package:yana/features/help/data/help_model.dart';
import 'package:yana/features/help/data/help_repository.dart';
import 'package:yana/features/help/logic/help_controller.dart';

class FakeHelpRepository extends HelpRepository {
  @override
  Future<List<HelpFacility>> getHelpFacilities() async {
    return [
      const HelpFacility(
        id: 1,
        name: 'YANA Test-Beratungsstelle',
        type: 'Beratungsstelle',
        address: 'Musterstraße 1',
        latitude: 49.0134,
        longitude: 12.1016,
        phone: null,
        email: null,
        openingHours: null,
        capacity: 10,
        categoryId: 1,
      ),
    ];
  }
}

class FailingHelpRepository extends HelpRepository {
  @override
  Future<List<HelpFacility>> getHelpFacilities() async {
    throw Exception('Verbindung fehlgeschlagen');
  }
}

void main() {
  test('HelpController startet ohne Daten', () {
    final controller = HelpController();

    expect(controller.facilities, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);

    controller.dispose();
  });

  test('HelpController lädt Hilfestellen erfolgreich', () async {
    final controller = HelpController(
      repository: FakeHelpRepository(),
    );

    await controller.loadFacilities();

    expect(controller.facilities.length, 1);
    expect(
      controller.facilities.first.name,
      'YANA Test-Beratungsstelle',
    );
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);

    controller.dispose();
  });

  test('HelpController behandelt Fehler korrekt', () async {
    final controller = HelpController(
      repository: FailingHelpRepository(),
    );

    await controller.loadFacilities();

    expect(controller.facilities, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNotNull);

    controller.dispose();
  });
}
