import 'package:bomcurriculo/util/Translation.dart';
import 'package:bomcurriculo/widget/WidgetButton.dart';
import 'package:flutter/material.dart';

import '../../include/Body.dart';

class ViewGenerateResume extends StatefulWidget {
  const ViewGenerateResume({super.key});
  @override
  _ViewGenerateResume createState() => _ViewGenerateResume();
}

class _ViewGenerateResume extends State<ViewGenerateResume> {
  //==========================
  // Dados pessoais
  //==========================

  List<Map<String, dynamic>> personalData = [
    {'title': 'Nome', 'value': 'Alexandre Martins', 'checked': true},
    {'title': 'Email', 'value': 'alexandre@email.com', 'checked': true},
    {'title': 'Phone', 'value': '(11) 99999-9999', 'checked': true},
    {'title': 'City', 'value': 'São Paulo - SP', 'checked': true},
    {
      'title': 'LinkedIn',
      'value': 'linkedin.com/in/alexandre',
      'checked': true,
    },
    {'title': 'GitHub', 'value': 'github.com/alexandre', 'checked': true},
  ];

  //==========================
  // Resumo
  //==========================

  List<Map<String, dynamic>> summary = [
    {
      'description':
          'Engenheiro de Software Sênior com mais de 8 anos de experiência em desenvolvimento Full Stack, arquitetura escalável, liderança técnica e otimização de performance.',
      'checked': true,
    },
  ];

  //==========================
  // Experiências
  //==========================

  List<Map<String, dynamic>> experiences = [
    {
      'title': 'Tech Lead & Full Stack Developer',
      'company': 'GlobalTech Solutions',
      'date_start': 'Jan/2020',
      'date_end': 'Atual',
      'checked': true,
    },
    {
      'title': 'Senior Software Engineer',
      'company': 'Innovation Hub',
      'date_start': 'Mar/2017',
      'date_end': 'Dez/2019',
      'checked': true,
    },
    {
      'title': 'Software Developer',
      'company': 'Soft Company',
      'date_start': 'Jan/2015',
      'date_end': 'Fev/2017',
      'checked': true,
    },
  ];

  //==========================
  // Formação
  //==========================

  List<Map<String, dynamic>> education = [
    {
      'title': 'Bacharelado em Ciência da Computação',
      'institution': 'Universidade Federal de São Paulo',
      'checked': true,
    },
    {
      'title': 'Pós-graduação em Engenharia de Software',
      'institution': 'USP',
      'checked': true,
    },
  ];

  //==========================
  // Cursos
  //==========================

  List<Map<String, dynamic>> courses = [
    {'title': 'Flutterando Masterclass', 'checked': true},
    {'title': 'Clean Architecture', 'checked': true},
    {'title': 'Git e GitHub', 'checked': true},
    {'title': 'Docker Essentials', 'checked': true},
  ];

  //==========================
  // Skills
  //==========================

  List<Map<String, dynamic>> skills = [
    {'title': 'Flutter', 'years': 4, 'checked': true},
    {'title': 'Dart', 'years': 4, 'checked': true},
    {'title': 'Firebase', 'years': 3, 'checked': true},
    {'title': 'REST API', 'years': 4, 'checked': true},
    {'title': 'Git', 'years': 6, 'checked': true},
  ];

  //==========================
  // Idiomas
  //==========================

  List<Map<String, dynamic>> languages = [
    {'title': 'Portuguese', 'level': 'Nativo', 'checked': true},
    {'title': 'English', 'level': 'Avançado', 'checked': true},
    {'title': 'Spanish', 'level': 'Intermediário', 'checked': true},
  ];

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
  }

  void generateResume() async {

  }

  @override
  Widget build(BuildContext context) {
    return Body(
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(15),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 10),

              Center(
                child: Text(
                  Translation.instance.translate('Review resume'),
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                ),
              ),

              const SizedBox(height: 10),

              Center(
                child: Text(
                  '${Translation.instance.translate('AI has prepared a resume for you')}.\n${Translation.instance.translate('Select the information you want to keep before generating the resume')}',
                  style: TextStyle(fontWeight: FontWeight(700)),
                  textAlign: TextAlign.center,
                ),
              ),

              const SizedBox(height: 25),

              //======================
              // DADOS PESSOAIS
              //======================
              Text(
                Translation.instance.translate('Personal data'),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 10),

              Column(
                children: personalData.map((personal) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        personal['checked'] = !personal['checked'];
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            personal['checked']
                                ? Icons.check_box_outlined
                                : Icons.check_box_outline_blank,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color(0xFFEEEEEE),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      Translation.instance.translate(personal['title']),
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                    Text(personal['value']),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              //======================
              // RESUMO
              //======================
              Text(
                Translation.instance.translate('Professional summary'),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 10),

              Column(
                children: summary.map((item) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        item['checked'] = !item['checked'];
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            item['checked']
                                ? Icons.check_box_outlined
                                : Icons.check_box_outline_blank,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color(0xFFEEEEEE),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Text(
                                  item['description'],
                                  style: const TextStyle(fontSize: 15),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              //======================
              // EXPERIÊNCIAS
              //======================
              Text(
                Translation.instance.translate('Professional experience'),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 10),

              Column(
                children: experiences.map((experience) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        experience['checked'] = !experience['checked'];
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            experience['checked']
                                ? Icons.check_box_outlined
                                : Icons.check_box_outline_blank,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color(0xFFEEEEEE),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      Translation.instance.translate(experience['title']),
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                    const SizedBox(height: 3),
                                    Text(experience['company'] ?? ''),
                                    const SizedBox(height: 3),
                                    Text(
                                      '${experience['date_start']} • ${experience['date_end']}',
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              //======================
              // FORMAÇÃO
              //======================
              Text(
                Translation.instance.translate('Education'),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 10),

              Column(
                children: education.map((item) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        item['checked'] = !item['checked'];
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            item['checked']
                                ? Icons.check_box_outlined
                                : Icons.check_box_outline_blank,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color(0xFFEEEEEE),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                        Translation.instance.translate(item['title']),
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 16,
                                        ),
                                    ),
                                    Text(item['institution']),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              //======================
              // CURSOS
              //======================
              Text(
                Translation.instance.translate('Courses'),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 10),

              Column(
                children: courses.map((course) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        course['checked'] = !course['checked'];
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        children: [
                          Icon(
                            course['checked']
                                ? Icons.check_box_outlined
                                : Icons.check_box_outline_blank,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color(0xFFEEEEEE),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Text(
                                  Translation.instance.translate(course['title']),
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              //======================
              // HABILIDADES
              //======================
              Text(
                Translation.instance.translate('Skills'),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 10),

              Column(
                children: skills.map((skill) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        skill['checked'] = !skill['checked'];
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            skill['checked']
                                ? Icons.check_box_outlined
                                : Icons.check_box_outline_blank,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color(0xFFEEEEEE),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      Translation.instance.translate(skill['title']),
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                    Text(
                                      '${skill['years']} anos de experiência',
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              //======================
              // IDIOMAS
              //======================
              Text(
                Translation.instance.translate('Languages'),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 10),

              Column(
                children: languages.map((language) {
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        language['checked'] = !language['checked'];
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        children: [
                          Icon(
                            language['checked']
                                ? Icons.check_box_outlined
                                : Icons.check_box_outline_blank,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: const Color(0xFFEEEEEE),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      Translation.instance.translate(language['title']),
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                    Text(language['level']),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 30),

              GestureDetector(
                onTap: generateResume,
                child: WidgetButton(title: Translation.instance.translate('Generate resume')),
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}