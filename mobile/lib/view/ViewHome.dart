import 'dart:convert';

import 'package:bomcurriculo/include/Navbar.dart';
import 'package:bomcurriculo/service/API.dart';
import 'package:bomcurriculo/util/Translation.dart';
import 'package:bomcurriculo/view/resume/ViewNewResume.dart';
import 'package:bomcurriculo/widget/WidgetButton.dart';
import 'package:bomcurriculo/widget/WidgetResume.dart';
import 'package:bomcurriculo/widget/WidgetScore.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../service/DB.dart';
import '../theme/AppColors.dart';

class ViewHome extends StatefulWidget {
  const ViewHome({super.key});
  @override
  State<ViewHome> createState() => _ViewHomeState();
}

class _ViewHomeState extends State<ViewHome> {
  bool loading = false;

  String name = '';
  String email = '';
  String emailVerifiedAt = '';
  String createdAt = '';
  String updatedAt = '';
  String githubLink = '';
  String siteLink = '';
  String socialName = '';
  String phone = '';
  String resume = '';
  String resumeEmail = '';
  String gender = '';
  bool isPcd = false;
  String city = '';
  String state = '';
  String country = '';
  String linkedinLink = '';

  /*
  var items = [
    {
      'type': 'fail',
      'title': '---',
      'subtitle': 'Falha ao processar currículo',
      'score': '---',
      'downloadURL': ''
    },
    {
      'type': 'pending',
      'title': '---',
      'subtitle': 'Currículo pendente - em processamento',
      'score': '---',
      'downloadURL': ''
    },
    {
      'type': 'analyze',
      'title': '---',
      'subtitle': 'Analisar currículo',
      'score': '---',
      'downloadURL': ''
    },
    {
      'type': 'ready',
      'title': 'Curriculo_ProductDesigner_v2.pdf',
      'subtitle': 'Atualizado há 2 dias',
      'score': '92',
      'downloadURL': ''
    }
    /*,
    {
      'type': 'ready',
      'title': 'Curriculo_ProductDesigner_v2.pdf',
      'subtitle': 'Atualizado há 2 dias',
      'score': '92',
      'downloadURL': ''
    }
     */
  ];

   */
  var items = [];

  void getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
    doAction();
  }

  void doAction() async {
    setState(() {
      loading = true;
    });

    try {
      //http://127.0.0.1:8000/api/client/resumes/files?type=cv
      var response = await API().get('client/user/resumes');
      //var response = await API().get('client/resumes/files?type=cv');
      var body = jsonDecode(response.body);

      //var userWebData = body['data']['user'];
      var userWebData = body['data']['data'];
      //var userWebData = body;

      print("*******************************");
      print(userWebData);
      print("*******************************");

      for (var data in userWebData) {
        String status = data['status'];
        String title = '---';
        String subtitle = 'Em  prsamento';
        String score = '---';
        if (status == 'pending') {
          subtitle = 'Em processamento';
        } else if (status == 'fail') {
          subtitle = 'Falha ao processar currículo';
        }
        items.add({
          'uuid': data['id'],
          'type': status,
          'title': title,
          'subtitle': subtitle,
          'score': score,
          'downloadURL': data['original_file_path_cv'],
        });
      }

      final user = await DB.instance.getUser();

      final userData = jsonDecode(user!);

      name = userData['name'] ?? '';
      email = userData['email'] ?? '';
      emailVerifiedAt = userData['email_verified_at'] ?? '';
      createdAt = userData['created_at'] ?? '';
      updatedAt = userData['updated_at'] ?? '';
      githubLink = userData['github_link'] ?? '';
      siteLink = userData['site_link'] ?? '';
      socialName = userData['social_name'] ?? '';
      phone = userData['phone'] ?? '';
      resume = userData['resume'] ?? '';
      resumeEmail = userData['resume_email'] ?? '';
      gender = userData['gender'] ?? '';
      isPcd = (userData['is_pcd'] ?? 0) == 1;
      city = userData['city'] ?? '';
      state = userData['state'] ?? '';
      country = userData['country'] ?? '';
      linkedinLink = userData['linkedin_link'] ?? '';
    } catch (e) {}

    setState(() {
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const Navbar(),
      body: loading
          ? Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(30.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        RichText(
                          text: TextSpan(
                            style: TextStyle(fontSize: 30, color: Colors.black),
                            children: [
                              TextSpan(
                                text:
                                    "${Translation.instance.translate('Welcome')}, ",
                                style: TextStyle(fontWeight: FontWeight(800)),
                              ),

                              TextSpan(
                                text: name,
                                style: TextStyle(
                                  color: AppColorsLight.brandPrimary,
                                  fontWeight: FontWeight(800),
                                ),
                              ),
                            ],
                          ),
                        ),
                        Text(
                          Translation.instance.translate(
                            'Seus Currículos otimizados em um só lugar',
                          ),
                          style: TextStyle(fontWeight: FontWeight(700)),
                        ),

                        const SizedBox(height: 15),

                        /*
                  Text(
                    Translation.instance.translate('My resumes'),
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 15.0),

                   */

                        //WidgetScore(),
                        Column(
                          children: items.map((item) {
                            return WidgetResume(
                              type: item['type'] ?? "",
                              title: item['title'] ?? "",
                              subtitle: item['subtitle'] ?? "",
                              score: item['score'] ?? "",
                              downloadURL: item['downloadURL'] ?? "",
                            );
                          }).toList(),
                        ),

                        items.length < 5
                            ? GestureDetector(
                                onTap: () {
                                  context.go("/resume/new-resume");
                                  //Navigator.push(
                                  //  context,
                                  //  MaterialPageRoute(
                                  //    builder: (context) => const ViewNewResume(),
                                  //  ),
                                  //);
                                },
                                child: WidgetButton(
                                  title: Translation.instance.translate(
                                    'Generate new resume',
                                  ),
                                ),
                              )
                            : SizedBox(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
