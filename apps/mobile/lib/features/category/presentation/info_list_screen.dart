import 'package:flutter/material.dart';

import '../../../core/network/api_client.dart';
import '../../../core/utils/phone_launcher.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/general_info_dropdown.dart';

class InfoListScreen extends StatefulWidget {
  const InfoListScreen({
    super.key,
    required this.title,
    required this.endpoint,
    this.info,
  });

  final String title;
  final String endpoint;
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
          if (widget.info != null) GeneralInfoDropdown(text: widget.info!),
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
          return ErrorView(onRetry: _reload);
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
