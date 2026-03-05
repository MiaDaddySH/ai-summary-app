import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _controller = TextEditingController();

  bool _hasText = false;
  String _summary = "";
  bool _loading = false;

  @override
  void initState() {
    super.initState();

    _controller.addListener(() {
      final hasText = _controller.text.isNotEmpty;
      if (hasText != _hasText) {
        setState(() {
          _hasText = hasText;
        });
      }
    });
  }

  Future<void> _summarize() async {
    final input = _controller.text.trim();
    if (input.isEmpty) return;

    setState(() {
      _loading = true;
      _summary = "";
    });

    try {
      final result = await ApiService.summarize(input);

      setState(() {
        _summary = result;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _summary = "Error: $e";
        _loading = false;
      });
    }
  }

  void _clearInput() {
    _controller.clear();
    setState(() {
      _hasText = false;
    });
  }

  void _copySummary() {
    if (_summary.isEmpty) return;

    Clipboard.setData(ClipboardData(text: _summary));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Summary copied")),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("AI Article Summary"),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              TextField(
                controller: _controller,
                decoration: InputDecoration(
                  labelText: "Paste article URL or text",
                  border: const OutlineInputBorder(),
                  suffixIcon: _hasText
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: _loading ? null : _clearInput,
                        )
                      : null,
                ),
                maxLines: 3,
                textInputAction: TextInputAction.done,
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _loading ? null : _summarize,
                  child: const Text("Summarize"),
                ),
              ),
              const SizedBox(height: 12),
              if (_loading)
                const Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 8),
                    Text("Summarizing article..."),
                  ],
                ),
              const SizedBox(height: 12),
              Expanded(
                child: _summary.isEmpty
                    ? const Center(
                        child: Text(
                          "Summary will appear here.",
                          textAlign: TextAlign.center,
                        ),
                      )
                    : Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  TextButton.icon(
                                    onPressed: _copySummary,
                                    icon: const Icon(Icons.copy),
                                    label: const Text("Copy"),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Expanded(
                                child: SingleChildScrollView(
                                  child: SelectableText(
                                    _summary,
                                    textAlign: TextAlign.left,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}