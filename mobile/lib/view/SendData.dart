import 'dart:io';

import 'package:bomcurriculo/include/Body.dart';
import 'package:bomcurriculo/widget/Button.dart';
import 'package:bomcurriculo/widget/ButtonIcon.dart';
import 'package:bomcurriculo/widget/InputText.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../widget/InputFile.dart';

class SendData extends StatefulWidget {
  const SendData({super.key});
  @override
  _SendData createState() => _SendData();
}

class _SendData extends State<SendData> {

  File? resumeFile;
  File? linkedinFile;
  String? resumeFileName;
  String? linkedinFileName;

  final List<TextEditingController> skills = [];

  @override
  void initState() {
    super.initState();
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

  void generateResume() {
    // Gerar currículo
  }

  @override
  Widget build(BuildContext context) {
    return Body(
      child: Padding(
        padding: const EdgeInsets.all(45.0),
        child: Column(
          children: [
            Text(
                'Fill data correctly to generate your resume',
                textAlign: TextAlign.center
            ),
            SizedBox(height: 30.0),
            InputFile(
              title: 'Your resume/CV',
              label: 'Choose a PDF file',
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
            InputFile(
              title: 'Linkedin resume',
              label: 'Choose a PDF file',
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
            InputText(title: 'GitHub URL',httpsPrefix: 'https://github.com/'),
            InputText(title: 'Your site URL',httpsPrefix: 'https://'),

            Column(
              children: List.generate(skills.length, (index) {
                return InputText(
                  title: 'Skill',
                  controller: skills[index],
                );
              }),
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