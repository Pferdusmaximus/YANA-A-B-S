import 'package:flutter/material.dart';

import 'app/profile_settings.dart';
import 'features/category/presentation/info_list_screen.dart';

class StartMenu extends StatelessWidget {
  const StartMenu({super.key});

  // (Titel, Endpoint, Allgemeine Informationen)
  static const _entries = <(String, String, String)>[
    (
      'Hilfenummern',
      '/hilfenummern',
      'Hilfenummern sind Telefonnummern, unter denen du schnell und meist '
          'kostenlos mit geschulten Beraterinnen und Beratern sprechen kannst.\n\n'
          'Wofür kann ich sie nutzen?\n'
          '• Wenn du akut Hilfe, Rat oder einfach jemanden zum Reden brauchst\n'
          '• Um dich über deine Möglichkeiten und nächste Schritte zu informieren\n'
          '• Um an passende Stellen in deiner Nähe weitervermittelt zu werden\n\n'
          'Viele Nummern sind rund um die Uhr erreichbar. In akuter Gefahr '
          'wähle bitte immer den Notruf 110 oder 112.',
    ),
    (
      'Anonyme Hilfestellen',
      '/anonyme-hilfestellen',
      'Anonyme Hilfestellen sind Beratungsangebote, bei denen du deinen Namen '
          'nicht nennen musst. Was du erzählst, bleibt vertraulich.\n\n'
          'Wofür kann ich sie nutzen?\n'
          '• Wenn du Hilfe suchst, aber (noch) nicht erkannt werden möchtest\n'
          '• Um deine Situation erst einmal unverbindlich zu schildern\n'
          '• Für Beratung per Telefon, Chat, E-Mail oder persönlich vor Ort\n\n'
          'Du entscheidest selbst, wie viel du erzählst und ob weitere '
          'Schritte folgen sollen.',
    ),
    (
      'Frauenhäuser',
      '/frauenhaeuser',
      'Frauenhäuser sind geschützte Einrichtungen, in denen Frauen (und ihre '
          'Kinder), die von Gewalt betroffen oder bedroht sind, vorübergehend '
          'sicher wohnen können. Die Adressen werden meist geheim gehalten.\n\n'
          'Wofür kann ich sie nutzen?\n'
          '• Als sicherer Zufluchtsort, wenn du zu Hause nicht sicher bist\n'
          '• Für Unterstützung und Beratung durch Fachkräfte\n'
          '• Für Hilfe bei Behördengängen, Finanzen, Wohnungssuche und rechtlichen Fragen\n\n'
          'Eine Aufnahme ist oft auch kurzfristig möglich – ruf am besten '
          'direkt an.',
    ),
    (
      'Psychische Unterstützung',
      '/psychische-unterstuetzung',
      'Psychische Unterstützung umfasst Angebote wie Krisendienste, '
          'psychologische Beratungsstellen, Seelsorge und Therapie.\n\n'
          'Wofür kann ich sie nutzen?\n'
          '• Wenn dich belastende Erlebnisse, Angst, Trauer oder Stress überfordern\n'
          '• Um Erlebtes zu verarbeiten und wieder Stabilität zu finden\n'
          '• In seelischen Krisen, auch kurzfristig und anonym\n\n'
          'Hilfe zu suchen ist kein Zeichen von Schwäche. Bei Gedanken, dir '
          'selbst etwas anzutun, wende dich bitte sofort an den Notruf 112.',
    ),
    (
      'Rechtliche Hilfe',
      '/rechtliche-hilfe',
      'Rechtliche Hilfe bekommst du bei Anwältinnen und Anwälten, '
          'Rechtsberatungsstellen und Opferhilfe-Organisationen.\n\n'
          'Wofür kann ich sie nutzen?\n'
          '• Um deine Rechte kennenzulernen, z. B. bei Gewalt, Trennung oder Sorgerecht\n'
          '• Für Fragen zu Anzeige, Schutzanordnungen oder Kontaktverboten\n'
          '• Für Begleitung und Vertretung in einem Gerichtsverfahren\n\n'
          'Wenn du wenig Geld hast, kannst du unter Umständen Beratungs- oder '
          'Prozesskostenhilfe erhalten.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Drawer(
      shape: const RoundedRectangleBorder(),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Startmenü',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              for (final (title, endpoint, info) in _entries)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Material(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(6),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(6),
                      onTap: () {
                        Navigator.pop(context); // Drawer schließen
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => InfoListScreen(
                              title: title,
                              endpoint: endpoint,
                              info: info,
                            ),
                          ),
                        );
                      },
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 14,
                        ),
                        child: Text(title),
                      ),
                    ),
                  ),
                ),
              const Spacer(),
              Align(
                alignment: Alignment.bottomRight,
                child: IconButton(
                  tooltip: 'Einstellungen',
                  icon: const Icon(Icons.settings),
                  onPressed: () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const SettingsScreen()),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}