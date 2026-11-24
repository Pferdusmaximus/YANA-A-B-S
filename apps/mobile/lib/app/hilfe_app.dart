import 'package:flutter/material.dart';

import '../frauenhaus.dart';
import '../hilfestellen.dart';
import '../hilfsnummern.dart';
import '../menu_ansicht.dart';
import '../psychische_hs.dart';
import '../rechtliche_hs.dart';
import 'app_shell.dart';
import 'app_theme.dart';

class HilfeApp extends StatelessWidget {
  const HilfeApp({super.key, this.initialRoute = '/'});

  final String initialRoute;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hilfe-App',
      debugShowCheckedModeBanner: false,
      initialRoute: initialRoute,
      routes: {
        '/': (_) => const HomeShell(),
        StartMenu.hilfenummern.$2: (_) =>
            HilfsnummernScreen(info: StartMenu.hilfenummern.$3),
        StartMenu.anonymeHilfestellen.$2: (_) => HelpFacilityScreen(
          title: StartMenu.anonymeHilfestellen.$1,
          info: StartMenu.anonymeHilfestellen.$3,
        ),
        '/frauenhaeuser': (_) => const FrauenhausScreen(),
        '/psychische-unterstuetzung': (_) => const PsychischeHilfeScreen(),
        '/rechtliche-hilfe': (_) => const RechtlicheHilfeScreen(),
      },
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: kPrimary),
        useMaterial3: true,
      ),
    );
  }
}
