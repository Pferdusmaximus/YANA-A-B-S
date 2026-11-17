import 'package:flutter/material.dart';

import 'app/app_theme.dart';
import 'core/utils/phone_launcher.dart';
import 'features/help/data/help_model.dart';
import 'features/help/data/help_repository.dart';
import 'shared/widgets/error_view.dart';
import 'shared/widgets/general_info_dropdown.dart';

class HelpFacilityScreen extends StatefulWidget {
  const HelpFacilityScreen({super.key, this.title = 'Hilfestellen', this.info});

  final String title;

  /// Text für das Dropdown „Allgemeine Informationen“ (optional).
  final String? info;

  @override
  State<HelpFacilityScreen> createState() => _HelpFacilityScreenState();
}

class _HelpFacilityScreenState extends State<HelpFacilityScreen> {
  static const _all = 'Alle';

  final HelpRepository _repository = HelpRepository();
  late Future<List<HelpFacility>> _future;

  String _query = '';
  String _selectedType = _all;

  @override
  void initState() {
    super.initState();
    _future = _repository.getHelpFacilities();
  }

  void _reload() {
    setState(() => _future = _repository.getHelpFacilities());
  }

  /// Zeilen, die nicht leer sind (funktioniert auch, wenn ein Feld null sein kann).
  List<String> _lines(HelpFacility f) => <String?>[
    f.type,
    f.address,
    f.openingHours,
  ].whereType<String>().where((s) => s.trim().isNotEmpty).toList();

  List<HelpFacility> _applyFilter(List<HelpFacility> all) {
    final q = _query.trim().toLowerCase();
    return all.where((f) {
      final matchesType = _selectedType == _all || f.type == _selectedType;
      final matchesQuery =
          q.isEmpty ||
          _lines(f).any((s) => s.toLowerCase().contains(q)) ||
          f.name.toLowerCase().contains(q);
      return matchesType && matchesQuery;
    }).toList();
  }

  void _showDetails(HelpFacility f) {
    final phone = f.phone;
    final hasPhone = phone != null && phone.isNotEmpty;
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: Colors.white,
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              f.name,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: yanaPurple,
              ),
            ),
            const SizedBox(height: 12),
            for (final line in _lines(f))
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 3),
                child: Text(line),
              ),
            if (hasPhone) ...[
              const SizedBox(height: 8),
              _InfoRow(icon: Icons.phone_outlined, text: phone),
              const SizedBox(height: 16),
              FilledButton.icon(
                style: FilledButton.styleFrom(
                  backgroundColor: yanaPurple,
                  minimumSize: const Size.fromHeight(48),
                ),
                onPressed: () => callNumber(phone),
                icon: const Icon(Icons.call),
                label: const Text('Anrufen'),
              ),
            ],
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: yanaBg,
      appBar: AppBar(
        backgroundColor: yanaBg,
        surfaceTintColor: Colors.transparent,
        centerTitle: true,
        title: Text(
          widget.title,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      body: Column(
        children: [
          if (widget.info != null) GeneralInfoDropdown(text: widget.info!),
          Expanded(
            child: FutureBuilder<List<HelpFacility>>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return ErrorView(onRetry: _reload);
                }
                final all = snapshot.data ?? [];
                if (all.isEmpty) {
                  return const Center(child: Text('Keine Einträge vorhanden.'));
                }

                // Filter-Chips ergeben sich aus den vorhandenen Typen.
                final types = <String>{
                  _all,
                  ...all.map((f) => f.type).whereType<String>(),
                }.toList();
                final facilities = _applyFilter(all);

                return Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                      child: TextField(
                        onChanged: (v) => setState(() => _query = v),
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
                        itemBuilder: (_, i) {
                          final t = types[i];
                          final selected = t == _selectedType;
                          return ChoiceChip(
                            label: Text(t),
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
                                setState(() => _selectedType = t),
                          );
                        },
                      ),
                    ),
                    Expanded(
                      child: facilities.isEmpty
                          ? const Center(
                              child: Padding(
                                padding: EdgeInsets.all(32),
                                child: Text(
                                  'Keine Hilfestelle gefunden. Versuche einen anderen Suchbegriff oder wähle „Alle“.',
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            )
                          : ListView.separated(
                              padding: const EdgeInsets.fromLTRB(
                                16,
                                12,
                                16,
                                16,
                              ),
                              itemCount: facilities.length,
                              separatorBuilder: (_, _) =>
                                  const Divider(height: 1),
                              itemBuilder: (context, i) {
                                final facility = facilities[i];
                                final phone = facility.phone;
                                return ListTile(
                                  contentPadding: const EdgeInsets.symmetric(
                                    vertical: 6,
                                  ),
                                  leading: const CircleAvatar(
                                    backgroundColor: yanaLight,
                                    child: Icon(
                                      Icons.place_outlined,
                                      color: yanaPurple,
                                    ),
                                  ),
                                  title: Text(
                                    facility.name,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  subtitle: Text(_lines(facility).join('\n')),
                                  isThreeLine: _lines(facility).length > 1,
                                  trailing: (phone != null && phone.isNotEmpty)
                                      ? IconButton(
                                          tooltip: 'Anrufen',
                                          icon: const Icon(
                                            Icons.call,
                                            color: yanaPurple,
                                          ),
                                          onPressed: () => callNumber(phone),
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
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: yanaPurple),
        const SizedBox(width: 10),
        Expanded(child: Text(text)),
      ],
    );
  }
}
