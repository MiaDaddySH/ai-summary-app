import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _controller = TextEditingController();

  String _summary = "";
  bool _loading = false;

  void _summarize() async {
    setState(() {
      _loading = true;
      _summary = "";
    });

    // 先模拟 API
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _summary = "This is a demo summary. Later we will connect the API.";
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("AI Article Summary"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [

            TextField(
              controller: _controller,
              decoration: const InputDecoration(
                labelText: "Paste article URL or text",
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),

            const SizedBox(height: 16),

            ElevatedButton(
              onPressed: _loading ? null : _summarize,
              child: const Text("Summarize"),
            ),

            const SizedBox(height: 20),

            if (_loading) const CircularProgressIndicator(),

            if (_summary.isNotEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(_summary),
                ),
              ),
          ],
        ),
      ),
    );
  }
}