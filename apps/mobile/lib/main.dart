import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import 'core/network/api_client.dart';
import 'features/help/data/help_model.dart';
import 'features/help/data/help_repository.dart';

const Color kPrimary = Color(0xFF7B1F6A); // Violett aus den Wireframes
const Color kDark = Color(0xFF454545);

void main() => runApp(const HilfeApp());

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------
class HilfeApp extends StatelessWidget {
  const HilfeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hilfe-App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: kPrimary),
        useMaterial3: true,
      ),
      home: const HomeShell(),
    );
  }
}

// ---------------------------------------------------------------------------
// Hilfsfunktionen
// ---------------------------------------------------------------------------
Future<void> callNumber(String number) async {
  final uri = Uri(scheme: 'tel', path: number);
  if (await canLaunchUrl(uri)) {
    await launchUrl(uri);
  }
}

// ---------------------------------------------------------------------------
// Shell: Home / Karte / Chatbot mit Bottom-Navigation + Startmenü (Drawer)
// ---------------------------------------------------------------------------
class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  int _index = 1; // 0 = Karte, 1 = Home, 2 = Hilfs-Bot

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      drawer: const StartMenu(),
      body: SafeArea(
        child: Column(
          children: [
            _TopBar(
              onMenu: () => _scaffoldKey.currentState?.openDrawer(),
              onProfile: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ProfileScreen()),
              ),
            ),
            Expanded(
              child: IndexedStack(
                index: _index,
                children: const [
                  MapPlaceholder(), // später: separates Karten-Modul
                  HomeView(),
                  ChatPlaceholder(), // später: separates Chatbot-Modul
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _BottomBar(
        index: _index,
        onChanged: (i) => setState(() => _index = i),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({required this.onMenu, required this.onProfile});

  final VoidCallback onMenu;
  final VoidCallback onProfile;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            tooltip: 'Menü',
            icon: const Icon(Icons.format_list_bulleted, size: 28),
            onPressed: onMenu,
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Colors.grey.shade600,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(6),
              ),
            ),
            onPressed: onProfile,
            child: const Text('Profil'),
          ),
        ],
      ),
    );
  }
}

class _BottomBar extends StatelessWidget {
  const _BottomBar({required this.index, required this.onChanged});

  final int index;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    Color colorFor(int i) => index == i ? Colors.red : kDark;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            IconButton(
              tooltip: 'Kartenansicht',
              iconSize: 30,
              icon: Icon(Icons.explore_outlined, color: colorFor(0)),
              onPressed: () => onChanged(0),
            ),
            IconButton(
              tooltip: 'Home',
              iconSize: 30,
              icon: Icon(Icons.home, color: colorFor(1)),
              onPressed: () => onChanged(1),
            ),
            IconButton(
              tooltip: 'Hilfs-Bot',
              iconSize: 30,
              icon: Icon(Icons.help, color: colorFor(2)),
              onPressed: () => onChanged(2),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Home Ansicht
// ---------------------------------------------------------------------------
class HomeView extends StatelessWidget {
  const HomeView({super.key});

  void _openList(BuildContext context, String title, String endpoint) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => InfoListScreen(title: title, endpoint: endpoint),
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
            label: 'Anonyme Hilfsnummern',
            onPressed: () => _openList(
              context,
              'Anonyme Hilfsnummern',
              '/anonyme-hilfsnummern',
            ),
          ),
          const SizedBox(height: 20),
          _WideButton(
            label: 'Hilfestellen',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const HelpFacilityScreen()),
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

// ---------------------------------------------------------------------------
// Menüansicht (Startmenü)
// ---------------------------------------------------------------------------
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

// ---------------------------------------------------------------------------
// Hilfestellen: lädt Einrichtungen über das HelpRepository (core/network)
// ---------------------------------------------------------------------------
class HelpFacilityScreen extends StatefulWidget {
  const HelpFacilityScreen({super.key});

  @override
  State<HelpFacilityScreen> createState() => _HelpFacilityScreenState();
}

class _HelpFacilityScreenState extends State<HelpFacilityScreen> {
  final HelpRepository _repository = HelpRepository();
  late Future<List<HelpFacility>> _future;

  @override
  void initState() {
    super.initState();
    _future = _repository.getHelpFacilities();
  }

  void _reload() {
    setState(() => _future = _repository.getHelpFacilities());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Hilfestellen')),
      body: FutureBuilder<List<HelpFacility>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return _ErrorView(onRetry: _reload);
          }
          final facilities = snapshot.data ?? [];
          if (facilities.isEmpty) {
            return const Center(child: Text('Keine Einträge vorhanden.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: facilities.length,
            separatorBuilder: (_, _) => const SizedBox(height: 8),
            itemBuilder: (context, i) {
              final facility = facilities[i];
              final phone = facility.phone;
              return Card(
                child: ListTile(
                  title: Text(facility.name),
                  subtitle: Text(
                    [
                      facility.type,
                      facility.address,
                      if (facility.openingHours != null) facility.openingHours!,
                    ].join('\n'),
                  ),
                  isThreeLine: true,
                  trailing: (phone != null && phone.isNotEmpty)
                      ? IconButton(
                          tooltip: 'Anrufen',
                          icon: const Icon(Icons.call),
                          onPressed: () => callNumber(phone),
                        )
                      : null,
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.onRetry});

  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Daten konnten nicht geladen werden.'),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: onRetry,
            child: const Text('Erneut versuchen'),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Generische Listenansicht: lädt Einträge über den ApiClient (core/network)
// ---------------------------------------------------------------------------
class InfoListScreen extends StatefulWidget {
  const InfoListScreen({
    super.key,
    required this.title,
    required this.endpoint,
    this.info,
  });

  final String title;
  final String endpoint;

  /// Optionaler Erklärtext, der oben fest als aufklappbares
  /// "Allgemeine Informationen"-Menü angezeigt wird.
  final String? info;

  @override
  State<InfoListScreen> createState() => _InfoListScreenState();
}

class _InfoListScreenState extends State<InfoListScreen> {
  final ApiClient _apiClient = ApiClient();
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _future = _fetchList();
  }

  Future<List<Map<String, dynamic>>> _fetchList() async {
    final data = await _apiClient.get(widget.endpoint);
    if (data is! List) {
      throw const FormatException('Unerwartetes Antwortformat der API');
    }
    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  void _reload() {
    setState(() => _future = _fetchList());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: Column(
        children: [
          if (widget.info != null) _GeneralInfoDropdown(text: widget.info!),
          Expanded(child: _buildList()),
        ],
      ),
    );
  }

  Widget _buildList() {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return _ErrorView(onRetry: _reload);
        }
        final items = snapshot.data ?? [];
        if (items.isEmpty) {
          return const Center(child: Text('Keine Einträge vorhanden.'));
        }
        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: items.length,
          separatorBuilder: (_, _) => const SizedBox(height: 8),
          itemBuilder: (context, i) {
            final item = items[i];
            final phone = item['telefon'] as String?;
            return Card(
              child: ListTile(
                title: Text('${item['name'] ?? ''}'),
                subtitle: Text('${item['beschreibung'] ?? ''}'),
                trailing: (phone != null && phone.isNotEmpty)
                    ? IconButton(
                        tooltip: 'Anrufen',
                        icon: const Icon(Icons.call),
                        onPressed: () => callNumber(phone),
                      )
                    : null,
              ),
            );
          },
        );
      },
    );
  }
}

// ---------------------------------------------------------------------------
// "Allgemeine Informationen": oben fest angezeigtes, aufklappbares Menü
// ---------------------------------------------------------------------------
class _GeneralInfoDropdown extends StatelessWidget {
  const _GeneralInfoDropdown({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Card(
        clipBehavior: Clip.antiAlias,
        margin: EdgeInsets.zero,
        child: ConstrainedBox(
          // Begrenzt die Höhe, damit die Liste darunter sichtbar bleibt.
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

// ---------------------------------------------------------------------------
// Platzhalter: Profil / Einstellungen
// ---------------------------------------------------------------------------
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Profil')),
    body: const Center(child: Text('Profil – folgt')),
  );
}

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Einstellungen')),
    body: const Center(child: Text('Einstellungen – folgen')),
  );
}

// ---------------------------------------------------------------------------
// Platzhalter für die separaten Module
// ---------------------------------------------------------------------------
class MapPlaceholder extends StatelessWidget {
  const MapPlaceholder({super.key});

  @override
  Widget build(BuildContext context) =>
      const Center(child: Text('Kartenansicht – separates Modul'));
}

class ChatPlaceholder extends StatelessWidget {
  const ChatPlaceholder({super.key});

  @override
  Widget build(BuildContext context) =>
      const Center(child: Text('Hilfs-Bot mit Chat – separates Modul'));
}
