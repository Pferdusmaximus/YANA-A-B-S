import 'package:flutter/material.dart';

import 'app/app_theme.dart';
import 'core/utils/phone_launcher.dart';
import 'features/category/presentation/info_list_screen.dart';
import 'hilfestellen.dart';
import 'menu_ansicht.dart';

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  /// Öffnet dieselbe Listenansicht wie der passende Eintrag im Startmenü
  /// (inkl. Dropdown „Allgemeine Informationen“).
  void _openList(BuildContext context, (String, String, String) entry) {
    final (title, endpoint, info) = entry;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) =>
            InfoListScreen(title: title, endpoint: endpoint, info: info),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Notfall
          SizedBox(
            width: 110,
            height: 110,
            child: FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: Colors.grey.shade600,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              onPressed: () => _showEmergencyDialog(context),
              child: const Text('Notfall'),
            ),
          ),
          const SizedBox(height: 56),
          _WideButton(
            label: 'Hilfsnummern',
            onPressed: () => _openList(context, StartMenu.hilfenummern),
          ),
          const SizedBox(height: 20),
          _WideButton(
            label: 'Anonyme Hilfestellen',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => HelpFacilityScreen(
                  title: StartMenu.anonymeHilfestellen.$1,
                  info: StartMenu.anonymeHilfestellen.$3,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showEmergencyDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Notfall'),
        content: const Text('Welchen Notruf möchtest du wählen?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => callNumber('110'),
            child: const Text('Polizei 110'),
          ),
          FilledButton(
            onPressed: () => callNumber('112'),
            child: const Text('Notarzt 112'),
          ),
        ],
      ),
    );
  }
}

class _WideButton extends StatelessWidget {
  const _WideButton({required this.label, required this.onPressed});

  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: FilledButton(
        style: FilledButton.styleFrom(
          backgroundColor: kDark,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
        onPressed: onPressed,
        child: Text(label),
      ),
    );
  }
}
