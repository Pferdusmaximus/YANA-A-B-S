import 'package:flutter/material.dart';

import '../../app/app_theme.dart';

/// Aufklappbare Karte „Allgemeine Informationen“ oben in einer Listenansicht.
class GeneralInfoDropdown extends StatelessWidget {
  const GeneralInfoDropdown({super.key, required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Card(
        clipBehavior: Clip.antiAlias,
        margin: EdgeInsets.zero,
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.of(context).size.height * 0.45,
          ),
          child: SingleChildScrollView(
            child: ExpansionTile(
              leading: const Icon(Icons.info_outline, color: kPrimary),
              title: const Text(
                'Allgemeine Informationen',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              shape: const Border(),
              collapsedShape: const Border(),
              childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              expandedCrossAxisAlignment: CrossAxisAlignment.start,
              children: [Text(text, style: const TextStyle(height: 1.4))],
            ),
          ),
        ),
      ),
    );
  }
}
