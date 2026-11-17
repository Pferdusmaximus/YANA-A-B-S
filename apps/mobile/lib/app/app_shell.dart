import 'package:flutter/material.dart';

import '../features/chatbot/chatbot.dart';
import '../features/map/map.dart';
import '../homeansicht.dart';
import '../menu_ansicht.dart';
import 'app_theme.dart';
import 'profile_settings.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  int _index = 1;

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
                  MapPlaceholder(),
                  HomeView(),
                  ChatPlaceholder(),
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
