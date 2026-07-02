
import 'package:bomcurriculo/widget/ButtonIcon.dart';
import 'package:flutter/material.dart';

import '../../include/Body.dart';
import '../../widget/Button.dart';

class GenerateResume extends StatefulWidget {
  const GenerateResume({super.key});
  @override
  _GenerateResume createState() => _GenerateResume();
}

class _GenerateResume extends State<GenerateResume> {

  List<Map<String,dynamic>> experiences = [
    {
      'title': 'Bom Currículo',
      'date_start': '02/06/2025',
      'date_end': '02/07/2026',
      'checked': true
    },
    {
      'title': 'Faculdade Uniasselvi',
      'date_start': '02/06/2025',
      'date_end': '02/07/2026',
      'checked': true
    },
    {
      'title': 'WhiteHats',
      'date_start': '02/06/2025',
      'date_end': '02/07/2026',
      'checked': true
    }
  ];

  List<Map<String,dynamic>> skills = [
    {
      'title': 'PHP',
      'years': 15,
      'checked': true
    },
    {
      'title': 'Laravel',
      'years': 8,
      'checked': true
    },
    {
      'title': 'React',
      'years': 5,
      'checked': true
    }
  ];

  void generateResume() {

  }

  @override
  Widget build(BuildContext context) {
    return Body(
      child: Padding(
        padding: const EdgeInsets.all(15.0),
        child: Column(
          children: [
            SizedBox(height: 10.0),
            Text(
                'Confirm your data to generate resume',
                style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.w600),
                textAlign: TextAlign.center
            ),
            SizedBox(height: 10.0),

            //Experiences
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Experiences'),
                SizedBox(height: 10.0),
                Column(
                  children: experiences.map((experience) {
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          experience['checked']=!experience['checked'];
                        });
                      },
                      child: Column(
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              ButtonIcon(icon: experience['checked']?Icons.check_box_outlined:Icons.check_box_outline_blank),
                              SizedBox(width: 5.0),
                              Expanded(
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: Color(0xFFEEEEEE),
                                    borderRadius: BorderRadius.circular(4.0)
                                  ),
                                  child: Padding(
                                    padding: const EdgeInsets.all(8.0),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(experience['title'], style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.w600)),
                                        Text('De: '+experience['date_start']+' à '+experience['date_end']),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 5.0)
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),

            SizedBox(height: 15.0),

            // Skills
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Skills'),
                SizedBox(height: 10.0),
                Column(
                  children: skills.map((skill) {
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          skill['checked']=!skill['checked'];
                        });
                      },
                      child: Column(
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              ButtonIcon(icon: skill['checked']?Icons.check_box_outlined:Icons.check_box_outline_blank),
                              SizedBox(width: 5.0),
                              Expanded(
                                child: Container(
                                  decoration: BoxDecoration(
                                      color: Color(0xFFEEEEEE),
                                      borderRadius: BorderRadius.circular(4.0)
                                  ),
                                  child: Padding(
                                    padding: const EdgeInsets.all(8.0),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(skill['title'], style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.w600)),
                                        Text('${skill['years']} anos de experiência'),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 5.0)
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),


            SizedBox(height: 15.0),

            GestureDetector(
                onTap: generateResume,
                child: Button(title: 'Generate resume')
            )
          ],
        ),
      ),
    );
  }
}
