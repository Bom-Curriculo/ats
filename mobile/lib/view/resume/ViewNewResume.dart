import 'dart:io';

import 'package:bomcurriculo/include/Body.dart';
import 'package:bomcurriculo/util/Translation.dart';
import 'package:bomcurriculo/view/ViewHome.dart';
import 'package:bomcurriculo/widget/WidgetButton.dart';
import 'package:bomcurriculo/widget/WidgetInputText.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../../service/API.dart';
import '../../widget/WidgetInputFile.dart';

class ViewNewResume extends StatefulWidget {
  const ViewNewResume({super.key});
  @override
  _ViewNewResume createState() => _ViewNewResume();
}

//processing, analyze, ready

class _ViewNewResume extends State<ViewNewResume> {
  File? resumeFile;
  File? linkedinFile;
  String? resumeFileName;
  String? linkedinFileName;

  final controllerGitHubURL = TextEditingController();
  final controllerWebsiteURL = TextEditingController();
  final List<TextEditingController> skills = [];

  Future<void> getTranslation() async {
    await Translation.instance.load("pt-BR");
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    getTranslation();
    addSkill();
  }

  void addSkill() {
    final controller = TextEditingController();

    void normalizeSkills() {
      bool hasEmpty = false;

      for (int i = skills.length - 1; i >= 0; i--) {
        if (skills[i].text.trim().isEmpty) {
          if (hasEmpty) {
            skills[i].dispose();
            skills.removeAt(i);
          } else {
            hasEmpty = true;
          }
        }
      }

      if (!hasEmpty) {
        addSkill();
        return;
      }

      setState(() {});
    }

    controller.addListener(() {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        normalizeSkills();
        if (skills.isNotEmpty &&
            controller == skills.last &&
            controller.text.trim().isNotEmpty) {
          addSkill();
        }
      });
    });

    // Atualiza controllers
    setState(() {
      skills.add(controller);
    });
  }

  @override
  void dispose() {
    for (final controller in skills) {
      controller.dispose();
    }
    super.dispose();
  }

  void validateResume() async {

    if (resumeFile == null || linkedinFile == null) {
      return;
    }

    final data = <String, String>{
      "github_link": controllerGitHubURL.text,
      "website_link": controllerWebsiteURL.text,
    };

    int skillIndex = 0;

    for (final controller in skills) {
      final skill = controller.text.trim();

      if (skill.isNotEmpty) {
        data["skills[$skillIndex][name]"] = skill;
        skillIndex++;
      }
    }

    final response = await API().upload(
      "client/resumes/new-resume",
      data,
      [
        {
          "field": "resume_cv",
          "path": resumeFile!.path,
        },
        {
          "field": "resume_linkedin",
          "path": linkedinFile!.path,
        },
      ],
    );
    print(response.body);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const ViewHome(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Body(
      child: Padding(
        padding: const EdgeInsets.all(45.0),
        child: Column(
          children: [
            Text(
              Translation.instance.translate('Fill data correctly to generate your resume'),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 30.0),
            WidgetInputFile(
              title: Translation.instance.translate('Your resume/CV'),
              label: Translation.instance.translate('Choose a PDF file'),
              fileName: resumeFileName,
              onTap: () async {
                FilePickerResult? result = await FilePicker.pickFiles(
                  type: FileType.custom,
                  allowedExtensions: ['pdf'],
                );
                if (result == null) {
                  return;
                }
                setState(() {
                  resumeFile = File(result.files.single.path!);
                  resumeFileName = result.files.single.name;
                });
              },
            ),
            WidgetInputFile(
              title: Translation.instance.translate('Linkedin resume'),
              label: Translation.instance.translate('Choose a PDF file'),
              fileName: linkedinFileName,
              onTap: () async {
                FilePickerResult? result = await FilePicker.pickFiles(
                  type: FileType.custom,
                  allowedExtensions: ['pdf'],
                );
                if (result == null) {
                  return;
                }
                setState(() {
                  linkedinFile = File(result.files.single.path!);
                  linkedinFileName = result.files.single.name;
                });
              },
            ),
            WidgetInputText(
                title: Translation.instance.translate('GitHub URL'),
                controller: controllerGitHubURL,
                httpsPrefix: 'https://github.com/'
            ),
            WidgetInputText(
                title: Translation.instance.translate('Your site URL'),
                controller: controllerWebsiteURL,
                httpsPrefix: 'https://'
            ),

            Column(
              children: List.generate(skills.length, (index) {
                return WidgetInputText(title: Translation.instance.translate('Skill'), controller: skills[index]);
              }),
            ),

            SizedBox(height: 15.0),

            GestureDetector(
              onTap: validateResume,
              child: WidgetButton(title: Translation.instance.translate('Validate resume')),
            ),
          ],
        ),
      ),
    );
  }
}