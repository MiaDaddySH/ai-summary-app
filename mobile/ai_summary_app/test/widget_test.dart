import 'package:flutter_test/flutter_test.dart';

import 'package:ai_summary_app/main.dart';

void main() {
  testWidgets('App loads home screen', (WidgetTester tester) async {

    // 启动 App
    await tester.pumpWidget(const AISummaryApp());

    // 检查标题是否存在
    expect(find.text('AI Article Summary'), findsOneWidget);

    // 检查按钮是否存在
    expect(find.text('Summarize'), findsOneWidget);
  });
}