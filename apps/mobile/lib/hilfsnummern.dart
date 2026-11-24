import 'package:flutter/material.dart';

import 'app/app_theme.dart';
import 'core/utils/phone_launcher.dart';
import 'features/emergency/data/emergency_model.dart';
import 'features/emergency/data/emergency_repository.dart';
import 'shared/widgets/error_view.dart';
import 'shared/widgets/general_info_dropdown.dart';

class HilfsnummernScreen extends StatefulWidget {
  const HilfsnummernScreen({super.key, this.info});

  final String? info;

  @override
  State<HilfsnummernScreen> createState() => _HilfsnummernScreenState();
}

class _HilfsnummernScreenState extends State<HilfsnummernScreen> {
  final EmergencyRepository _repository = EmergencyRepository();
  late Future<List<EmergencyContact>> _future;
  String _query = '';
  String _selectedAvailability = 'Alle';

  @override
  void initState() {
    super.initState();
    _future = _repository.getEmergencyContacts();
  }

  void _reload() {
    setState(() => _future = _repository.getEmergencyContacts());
  }

  List<EmergencyContact> _filter(List<EmergencyContact> contacts) {
    final query = _query.trim().toLowerCase();
    return contacts.where((contact) {
      final matchesAvailability =
          _selectedAvailability == 'Alle' ||
          contact.availability == _selectedAvailability;
      final matchesQuery =
          query.isEmpty ||
          <String>[
            contact.name,
            contact.phoneNumber,
            contact.description,
            contact.availability,
          ].any((value) => value.toLowerCase().contains(query));
      return matchesAvailability && matchesQuery;
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
          'Hilfsnummern',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      body: Column(
        children: [
          if (widget.info != null) GeneralInfoDropdown(text: widget.info!),
          Expanded(
            child: FutureBuilder<List<EmergencyContact>>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return ErrorView(onRetry: _reload);
                }
                final contacts = snapshot.data ?? [];
                if (contacts.isEmpty) {
                  return const Center(child: Text('Keine Einträge vorhanden.'));
                }

                final availabilities = <String>{
                  'Alle',
                  ...contacts.map((contact) => contact.availability),
                }.toList();
                final filteredContacts = _filter(contacts);

                return Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                      child: TextField(
                        onChanged: (value) => setState(() => _query = value),
                        decoration: InputDecoration(
                          hintText: 'Suche nach Name, Nummer oder Thema …',
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
                        itemCount: availabilities.length,
                        separatorBuilder: (_, _) => const SizedBox(width: 8),
                        itemBuilder: (_, index) {
                          final availability = availabilities[index];
                          final selected =
                              availability == _selectedAvailability;
                          return ChoiceChip(
                            label: Text(availability),
                            selected: selected,
                            showCheckmark: false,
                            selectedColor: yanaPurple,
                            backgroundColor: yanaLight,
                            side: BorderSide.none,
                            labelStyle: TextStyle(
                              color: selected ? Colors.white : yanaPurple,
                              fontWeight: FontWeight.w600,
                            ),
                            onSelected: (_) => setState(
                              () => _selectedAvailability = availability,
                            ),
                          );
                        },
                      ),
                    ),
                    Expanded(
                      child: filteredContacts.isEmpty
                          ? const Center(
                              child: Padding(
                                padding: EdgeInsets.all(32),
                                child: Text(
                                  'Keine Hilfsnummer gefunden. Versuche einen '
                                  'anderen Suchbegriff oder wähle „Alle“.',
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
                              itemCount: filteredContacts.length,
                              separatorBuilder: (_, _) =>
                                  const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final contact = filteredContacts[index];
                                return ListTile(
                                  contentPadding: const EdgeInsets.symmetric(
                                    vertical: 6,
                                  ),
                                  leading: const CircleAvatar(
                                    backgroundColor: yanaLight,
                                    child: Icon(
                                      Icons.phone_outlined,
                                      color: yanaPurple,
                                    ),
                                  ),
                                  title: Text(
                                    contact.name,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  subtitle: Text(
                                    '${contact.phoneNumber}\n'
                                    '${contact.availability}',
                                  ),
                                  isThreeLine: true,
                                  trailing: IconButton(
                                    tooltip: 'Anrufen',
                                    icon: const Icon(
                                      Icons.call,
                                      color: yanaPurple,
                                    ),
                                    onPressed: () =>
                                        callNumber(contact.phoneNumber),
                                  ),
                                  onTap: () => _showDetails(contact),
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

  void _showDetails(EmergencyContact contact) {
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
              contact.name,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: yanaPurple,
              ),
            ),
            const SizedBox(height: 12),
            Text(contact.description),
            const SizedBox(height: 8),
            Text('Erreichbarkeit: ${contact.availability}'),
            const SizedBox(height: 16),
            FilledButton.icon(
              style: FilledButton.styleFrom(
                backgroundColor: yanaPurple,
                minimumSize: const Size.fromHeight(48),
              ),
              onPressed: () => callNumber(contact.phoneNumber),
              icon: const Icon(Icons.call),
              label: const Text('Anrufen'),
            ),
          ],
        ),
      ),
    );
  }
}
