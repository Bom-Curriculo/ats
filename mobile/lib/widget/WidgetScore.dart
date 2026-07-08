
import 'package:flutter/material.dart';

import '../util/Translation.dart';

class WidgetScore extends StatefulWidget {
  const WidgetScore({super.key});
  @override
  _WidgetScore createState() => _WidgetScore();
}

class _WidgetScore extends State<WidgetScore> {

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
  }


  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ATS SCORE
                  Container(
                    width: 90,
                    height: 90,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: Colors.blue,
                        width: 5,
                      ),
                    ),
                    child: const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            "85",
                            style: TextStyle(
                              fontSize: 30,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            "ATS SCORE",
                            style: TextStyle(fontSize: 10),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(width: 20),

                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade50,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            Translation.instance.translate('GLOBAL MEDIA'),
                            style: TextStyle(
                              color: Colors.blue,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),

                        const SizedBox(height: 8),

                        Text(
                          Translation.instance.translate('General performance'),
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),

                        const SizedBox(height: 8),

                        Text(
                          Translation.instance.translate('Your medium score are excelent'),
                        ),

                        const SizedBox(height: 4),

                        Text(
                          Translation.instance.translate('Focus on adding keywords specific to Product Designer roles to achieve the maximum score'),
                        ),

                        const SizedBox(height: 12),

                        Wrap(
                          spacing: 5,
                          children: [
                            Chip(
                              padding: const EdgeInsets.all(2.0),
                              label: Text(Translation.instance.translate('Keywords')),
                              backgroundColor: Colors.blue.shade50,
                            ),
                            Chip(
                              padding: const EdgeInsets.all(2.0),
                              label: Text(Translation.instance.translate('Formatting')),
                              backgroundColor: Colors.blue.shade50,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 15),
      ],
    );
  }
}
