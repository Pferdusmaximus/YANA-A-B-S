import 'package:flutter/material.dart';

import 'app/app_theme.dart';
import 'core/utils/phone_launcher.dart';
import 'menu_ansicht.dart';

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 24),
        child: Column(
          children: [
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
            const SizedBox(height: 32),
            _WideButton(
              label: 'Hilfsnummern',
              onPressed: () =>
                  Navigator.pushNamed(context, StartMenu.hilfenummern.$2),
            ),
            const SizedBox(height: 12),
            _WideButton(
              label: 'Frauenhäuser',
              onPressed: () => Navigator.pushNamed(context, '/frauenhaeuser'),
            ),
            const SizedBox(height: 12),
            _WideButton(
              label: 'Psychische Unterstützung',
              onPressed: () =>
                  Navigator.pushNamed(context, '/psychische-unterstuetzung'),
            ),
            const SizedBox(height: 12),
            _WideButton(
              label: 'Rechtliche Hilfe',
              onPressed: () =>
                  Navigator.pushNamed(context, '/rechtliche-hilfe'),
            ),
            const SizedBox(height: 12),
            _WideButton(
              label: 'Anonyme Hilfestellen',
              onPressed: () => Navigator.pushNamed(
                context,
                StartMenu.anonymeHilfestellen.$2,
              ),
            ),
          ],
        ),
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
