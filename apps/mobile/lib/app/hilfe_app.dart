import 'package:flutter/material.dart';

import 'app_shell.dart';
import 'app_theme.dart';

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
