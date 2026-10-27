import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

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
// API-Service (FastAPI -> PostgreSQL)
// ---------------------------------------------------------------------------
class ApiService {
  /// Erwartet eine JSON-Liste, z. B.
  /// [{"name": "...", "beschreibung": "...", "telefon": "...", "website": "..."}]
  static Future<List<Map<String, dynamic>>> fetchList(String endpoint) async {
    final response = await http
        .get(Uri.parse('$apiBaseUrl$endpoint'))
        .timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      throw Exception('Serverfehler (${response.statusCode})');
    }
    final data = jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    return data.cast<Map<String, dynamic>>();
  }
}

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
            onPressed: () => _openList(context, 'Hilfestellen', '/hilfestellen'),
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
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(6),
          ),
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

  static const _entries = <(String, String)>[
    ('Hilfenummern', '/hilfenummern'),
    ('Anonyme Hilfestellen', '/anonyme-hilfestellen'),
    ('Frauenhäuser', '/frauenhaeuser'),
    ('Psychische Unterstützung', '/psychische-unterstuetzung'),
    ('Rechtliche Hilfe', '/rechtliche-hilfe'),
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
              for (final (title, endpoint) in _entries)
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
// Generische Listenansicht: lädt Einträge per FastAPI aus PostgreSQL
// ---------------------------------------------------------------------------
class InfoListScreen extends StatefulWidget {
  const InfoListScreen({
    super.key,
    required this.title,
    required this.endpoint,
  });

  final String title;
  final String endpoint;

  @override
  State<InfoListScreen> createState() => _InfoListScreenState();
}

class _InfoListScreenState extends State<InfoListScreen> {
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _future = ApiService.fetchList(widget.endpoint);
  }

  void _reload() {
    setState(() => _future = ApiService.fetchList(widget.endpoint));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Daten konnten nicht geladen werden.'),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: _reload,
                    child: const Text('Erneut versuchen'),
                  ),
                ],
              ),
            );
          }
          final items = snapshot.data ?? [];
          if (items.isEmpty) {
            return const Center(child: Text('Keine Einträge vorhanden.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
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