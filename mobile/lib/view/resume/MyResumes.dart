
import 'package:bomcurriculo/widget/ButtonIcon.dart';
import 'package:flutter/material.dart';

import '../../include/Body.dart';

class MyResumes extends StatefulWidget {
  const MyResumes({super.key});
  @override
  _MyResumes createState() => _MyResumes();
}

class _MyResumes extends State<MyResumes> {

  List<Map<String,dynamic>> resumes = [
    {
      'title': 'Currículo 1',
      'datetime': '02/07/2026 12:34'
    },
    {
      'title': 'Currículo 1',
      'datetime': '02/07/2026 12:34'
    },
    {
      'title': 'Currículo 1',
      'datetime': '02/07/2026 12:34'
    },
    {
      'title': 'Currículo 1',
      'datetime': '02/07/2026 12:34'
    }
  ];

  @override
  Widget build(BuildContext context) {
    return Body(
      child: Padding(
        padding: const EdgeInsets.all(15.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
                'Meus currículos',
                style: TextStyle(
                  fontSize: 16.0
                ),
                textAlign: TextAlign.center
            ),
            SizedBox(height: 15.0),

            // Skills
            Column(
              children: resumes.map((resume) {
                return Column(
                  children: [
                    Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: Color(0xFFEEEEEE),
                        borderRadius: BorderRadius.circular(4.0)
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(resume['title'],style: TextStyle(
                                      fontSize:18.0,
                                      fontWeight: FontWeight.w600
                                  )),
                                  Text(resume['datetime']),
                                ],
                              ),
                            ),
                            ButtonIcon(icon: Icons.file_download_sharp)
                          ],
                        ),
                      ),
                    ),
                    SizedBox(height: 5.0)
                  ],
                );
              }).toList(),
            ),

            SizedBox(height: 15.0),

          ],
        ),
      ),
    );
  }
}
