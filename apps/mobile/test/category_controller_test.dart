import 'package:flutter_test/flutter_test.dart';

import 'package:yana/features/category/data/category_model.dart';
import 'package:yana/features/category/data/category_repository.dart';
import 'package:yana/features/category/logic/category_controller.dart';

class FakeCategoryRepository extends CategoryRepository {
  @override
  Future<List<YanaCategory>> getCategories() async {
    return [
      const YanaCategory(
        id: 1,
        name: 'Frauenberatung',
        description: 'Beratungsangebote für Frauen',
      ),
    ];
  }
}

class FailingCategoryRepository extends CategoryRepository {
  @override
  Future<List<YanaCategory>> getCategories() async {
    throw Exception('Verbindung fehlgeschlagen');
  }
}

void main() {
  test('CategoryController startet ohne Daten', () {
    final controller = CategoryController();

    expect(controller.categories, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);

    controller.dispose();
  });

  test('CategoryController lädt Kategorien erfolgreich', () async {
    final controller = CategoryController(
      repository: FakeCategoryRepository(),
    );

    await controller.loadCategories();

    expect(controller.categories.length, 1);
    expect(controller.categories.first.name, 'Frauenberatung');
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNull);

    controller.dispose();
  });

  test('CategoryController behandelt Fehler', () async {
    final controller = CategoryController(
      repository: FailingCategoryRepository(),
    );

    await controller.loadCategories();

    expect(controller.categories, isEmpty);
    expect(controller.isLoading, false);
    expect(controller.errorMessage, isNotNull);

    controller.dispose();
  });
}