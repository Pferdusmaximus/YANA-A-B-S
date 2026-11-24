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
        padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 24),
        child: Column(
          children: [
            SizedBox(
              width: 220,
              height: 220,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  textStyle: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
                  backgroundColor: const Color.fromARGB(255, 198, 8, 8),
                  shape: CircleBorder(
                    side: BorderSide(
                      color: const Color.fromARGB(255, 146, 0, 0),
                      width: 4,
                    ),
                  
                  ),
                ),
                onPressed: () => _showEmergencyDialog(context),
                child: const Text('Notfall'),
              ),
            ),
            const SizedBox(height: 80),
            _WideButton(
              label: 'Hilfsnummern',
              onPressed: () =>
                  Navigator.pushNamed(context, StartMenu.hilfenummern.$2),
            ),

            const SizedBox(height: 15),
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
