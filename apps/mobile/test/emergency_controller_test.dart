import 'package:flutter_test/flutter_test.dart';

import 'package:yana/features/emergency/data/emergency_model.dart';
import 'package:yana/features/emergency/data/emergency_repository.dart';
import 'package:yana/features/emergency/logic/emergency_controller.dart';

class FakeEmergencyRepository extends EmergencyRepository {
  @override
  Future<List<EmergencyContact>> getEmergencyContacts() async {
    return [
      const EmergencyContact(
        id: 1,
        name: 'YANA Testkontakt',
        phoneNumber: '000000',
        categoryId: 1,
        description: 'Fiktiver Kontakt für automatisierte Tests',
        availability: 'Testdaten',
      ),
    ];
  }
}

class FailingEmergencyRepository extends EmergencyRepository {
  @override
  Future<List<EmergencyContact>> getEmergencyContacts() async {
    throw Exception('Verbindung fehlgeschlagen');
  }
}

void main() {
  test('EmergencyController startet ohne Daten', () {
    final controller = EmergencyController();

    expect(controller.contacts, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);

    controller.dispose();
  });

  test('EmergencyController lädt Notfallnummern erfolgreich', () async {
    final controller = EmergencyController(
      repository: FakeEmergencyRepository(),
    );

    await controller.loadContacts();

    expect(controller.contacts.length, 1);
    expect(controller.contacts.first.name, 'YANA Testkontakt');
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);

    controller.dispose();
  });

  test('EmergencyController behandelt Fehler', () async {
    final controller = EmergencyController(
      repository: FailingEmergencyRepository(),
    );

    await controller.loadContacts();

    expect(controller.contacts, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNotNull);

    controller.dispose();
  });
}