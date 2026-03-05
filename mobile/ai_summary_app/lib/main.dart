import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const AISummaryApp());
}

class AISummaryApp extends StatelessWidget {
  const AISummaryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Summary',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomeScreen(),
    );
  }
}