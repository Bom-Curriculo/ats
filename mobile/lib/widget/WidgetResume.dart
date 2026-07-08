
import 'package:bomcurriculo/view/resume/ViewGenerateResume.dart';
import 'package:flutter/material.dart';

import '../service/API.dart';

class WidgetResume extends StatefulWidget {
  const WidgetResume({
    super.key,
    required this.type,
    required this.title,
    required this.subtitle,
    required this.score,
    required this.downloadURL
  });

  final String type; // pending, analyze, ready, fail
  final String title;
  final String subtitle;
  final String score;
  final String downloadURL;

  @override
  _WidgetResume createState() => _WidgetResume();
}

class _WidgetResume extends State<WidgetResume> {

  @override
  Widget build(BuildContext context) {

    IconData icon = Icons.access_time_sharp;
    Color? color = Colors.black12;
    Color? colorBorder = Colors.grey.shade300;
    if (widget.type=="pending") {
      color = Color(0x09000000);
    } else if (widget.type=="analyze") {
      color = Color(0x33ffff00);
      colorBorder = Color(0x77cccc00);
      icon = Icons.chevron_right;
    } else if (widget.type=="ready") {
      color = Colors.white;
      icon = Icons.download;
    } else if (widget.type=="fail") {
      color = Color(0x22ff0000);
      colorBorder = Color(0x22cc0000);
    }

    return GestureDetector(
      onTap: () async {
        if (widget.type=='analyze') {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ViewGenerateResume(),
            ),
          );
        } else if (widget.type=='ready') {
            final file = await API().download(
              widget.downloadURL,
            );
            print(file.path);
        }
      },
      child: Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color,
              border: Border.all(color: colorBorder),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.description_outlined,
                      size: 40,
                      color: Colors.blueGrey,
                    ),
                    const Spacer(),
                    Column(
                      children: [
                        Text(
                          widget.score.toString(),
                          style: TextStyle(
                            color: widget.type=="ready"?Colors.blue:Color(0xff999999),
                            fontSize: 26,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          "SCORE",
                          style: TextStyle(fontSize: 10),
                        ),
                      ],
                    ),
                    SizedBox(width: 4.0),
                  ],
                ),
                const SizedBox(height: 5),
                Row(
                  children: [
                    SizedBox(width: 8.0),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.title,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 5),
                          Text(
                            widget.subtitle,
                            style: TextStyle(color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
                    Column(
                      children: [
                        SizedBox(height: 10),
                        Icon(icon),
                      ],
                    )
                  ],
                ),
                /*
                Row(
                  children: [
                    Icon(Icons.language, size: 16),
                    SizedBox(width: 5),
                    Text("pt-BR"),
                    Spacer(),
                    GestureDetector(
                      onTap: () async {
                        final file = await API().download(
                          widget.downloadURL,
                        );
                        print(file.path);
                      },
                      child: Icon(icon)
                    ),
                  ],
                ),

                 */
              ],
            ),
          ),
          const SizedBox(height: 15),
        ],
      ),
    );
  }
}