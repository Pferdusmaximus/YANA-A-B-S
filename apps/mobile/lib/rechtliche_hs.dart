import 'package:flutter/material.dart';

import 'app/app_theme.dart';
import 'core/utils/phone_launcher.dart';
import 'features/category/data/category_model.dart';
import 'features/category/data/category_repository.dart';
import 'features/help/data/help_model.dart';
import 'features/help/data/help_repository.dart';
import 'shared/widgets/error_view.dart';
import 'shared/widgets/general_info_dropdown.dart';

class RechtlicheHilfeScreen extends StatefulWidget {
  const RechtlicheHilfeScreen({super.key});

  @override
  State<RechtlicheHilfeScreen> createState() => _RechtlicheHilfeScreenState();
}

class _RechtlicheHilfeScreenState extends State<RechtlicheHilfeScreen> {
  static const _keywords = [
    'recht',
    'anwalt',
    'rechtsberatung',
    'opferhilfe',
    'gericht',
  ];
  final HelpRepository _helpRepository = HelpRepository();
  final CategoryRepository _categoryRepository = CategoryRepository();
  late Future<List<HelpFacility>> _future;
  String _query = '';
  String _selectedType = 'Alle';

  @override
  void initState() {
    super.initState();
    _future = _loadFacilities();
  }

  Future<List<HelpFacility>> _loadFacilities() async {
    final results = await Future.wait([
      _helpRepository.getHelpFacilities(),
      _categoryRepository.getCategories(),
    ]);
    final facilities = results[0] as List<HelpFacility>;
    final categories = results[1] as List<YanaCategory>;
    final categoryIds = categories
        .where(
          (category) => _keywords.any(
            (word) => '${category.name} ${category.description ?? ''}'
                .toLowerCase()
                .contains(word),
          ),
        )
        .map((category) => category.id)
        .toSet();

    return facilities.where((facility) {
      final categoryMatches = categoryIds.contains(facility.categoryId);
      final textMatches = _keywords.any(
        (word) =>
            '${facility.type} ${facility.name}'.toLowerCase().contains(word),
      );
      return categoryMatches || textMatches;
    }).toList();
  }

  void _reload() {
    setState(() => _future = _loadFacilities());
  }

  List<HelpFacility> _filter(List<HelpFacility> facilities) {
    final query = _query.trim().toLowerCase();
    return facilities.where((facility) {
      final matchesType =
          _selectedType == 'Alle' || facility.type == _selectedType;
      final matchesQuery =
          query.isEmpty ||
          <String?>[
            facility.name,
            facility.type,
            facility.address,
            facility.openingHours,
          ].whereType<String>().any(
            (value) => value.toLowerCase().contains(query),
          );
      return matchesType && matchesQuery;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: yanaBg,
      appBar: AppBar(
        backgroundColor: yanaBg,
        surfaceTintColor: Colors.transparent,
        centerTitle: true,
        title: const Text(
          'Rechtliche Hilfe',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      body: Column(
        children: [
          const GeneralInfoDropdown(
            text:
                'Beratungsstellen und Fachkräfte können dich über deine '
                'Rechte und mögliche Schutzmaßnahmen informieren. Je nach '
                'Situation ist auch eine kostenlose oder vergünstigte '
                'Beratung möglich.',
          ),
          Expanded(
            child: FutureBuilder<List<HelpFacility>>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) return ErrorView(onRetry: _reload);

                final facilities = snapshot.data ?? [];
                if (facilities.isEmpty) {
                  return const Center(child: Text('Keine Einträge vorhanden.'));
                }
                final types = <String>{
                  'Alle',
                  ...facilities.map((facility) => facility.type),
                }.toList();
                final filtered = _filter(facilities);

                return Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                      child: TextField(
                        onChanged: (value) => setState(() => _query = value),
                        decoration: InputDecoration(
                          hintText: 'Suche nach Name, Ort oder Thema …',
                          prefixIcon: const Icon(Icons.search),
                          filled: true,
                          fillColor: Colors.white,
                          contentPadding: EdgeInsets.zero,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide: const BorderSide(color: yanaLight),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide: const BorderSide(color: yanaLight),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      height: 44,
                      child: ListView.separated(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        itemCount: types.length,
                        separatorBuilder: (_, _) => const SizedBox(width: 8),
                        itemBuilder: (_, index) {
                          final type = types[index];
                          final selected = type == _selectedType;
                          return ChoiceChip(
                            label: Text(type),
                            selected: selected,
                            showCheckmark: false,
                            selectedColor: yanaPurple,
                            backgroundColor: yanaLight,
                            side: BorderSide.none,
                            labelStyle: TextStyle(
                              color: selected ? Colors.white : yanaPurple,
                              fontWeight: FontWeight.w600,
                            ),
                            onSelected: (_) =>
                                setState(() => _selectedType = type),
                          );
                        },
                      ),
                    ),
                    Expanded(
                      child: filtered.isEmpty
                          ? const Center(
                              child: Text(
                                'Keine passende Hilfestelle gefunden.',
                              ),
                            )
                          : ListView.separated(
                              padding: const EdgeInsets.fromLTRB(
                                16,
                                12,
                                16,
                                16,
                              ),
                              itemCount: filtered.length,
                              separatorBuilder: (_, _) =>
                                  const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final facility = filtered[index];
                                return ListTile(
                                  contentPadding: const EdgeInsets.symmetric(
                                    vertical: 6,
                                  ),
                                  leading: const CircleAvatar(
                                    backgroundColor: yanaLight,
                                    child: Icon(
                                      Icons.gavel_outlined,
                                      color: yanaPurple,
                                    ),
                                  ),
                                  title: Text(
                                    facility.name,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  subtitle: Text(
                                    [
                                      facility.type,
                                      facility.address,
                                      facility.openingHours,
                                    ].whereType<String>().join('\n'),
                                  ),
                                  trailing: facility.phone?.isNotEmpty == true
                                      ? IconButton(
                                          tooltip: 'Anrufen',
                                          icon: const Icon(
                                            Icons.call,
                                            color: yanaPurple,
                                          ),
                                          onPressed: () =>
                                              callNumber(facility.phone!),
                                        )
                                      : const Icon(Icons.chevron_right),
                                  onTap: () => _showDetails(facility),
                                );
                              },
                            ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _showDetails(HelpFacility facility) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: Colors.white,
      builder: (context) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              facility.name,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: yanaPurple,
              ),
            ),
            const SizedBox(height: 12),
            for (final value in <String?>[
              facility.type,
              facility.address,
              facility.openingHours,
            ])
              if (value != null && value.trim().isNotEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 3),
                  child: Text(value),
                ),
            if (facility.phone?.isNotEmpty == true) ...[
              const SizedBox(height: 16),
              FilledButton.icon(
                style: FilledButton.styleFrom(
                  backgroundColor: yanaPurple,
                  minimumSize: const Size.fromHeight(48),
                ),
                onPressed: () => callNumber(facility.phone!),
                icon: const Icon(Icons.call),
                label: const Text('Anrufen'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
