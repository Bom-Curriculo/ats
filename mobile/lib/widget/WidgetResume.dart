
import 'package:flutter/material.dart';

import '../service/API.dart';

class WidgetResume extends StatefulWidget {
  const WidgetResume({
    super.key,
    required this.title,
    required this.subtitle,
    required this.score,
    required this.downloadURL
  });

  final String title;
  final String subtitle;
  final int score;
  final String downloadURL;

  @override
  _WidgetResume createState() => _WidgetResume();
}

class _WidgetResume extends State<WidgetResume> {

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
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
                      color: Colors.blue,
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
            ],
          ),
          const SizedBox(height: 15),
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
          const SizedBox(height: 15),
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
                child: Icon(Icons.download)
              ),
            ],
          ),
        ],
      ),
    );
  }
}