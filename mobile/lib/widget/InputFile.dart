import 'package:flutter/material.dart';

class InputFile extends StatefulWidget {
  const InputFile({
    super.key,
    this.title = '',
    this.label = 'Select a file',
    this.onTap,
    this.fileName,
  });

  final String title;
  final String label;
  final String? fileName;
  final VoidCallback? onTap;

  @override
  State<InputFile> createState() => _InputFile();
}

class _InputFile extends State<InputFile> {
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.title,
            style: const TextStyle(
              fontSize: 16.0,
            ),
          ),
          const SizedBox(height: 5.0),
          GestureDetector(
            onTap: widget.onTap,
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: const Color(0xFFEEEEEE),
                borderRadius: BorderRadius.circular(4.0),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12.0,
                  vertical: 12.0,
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.upload_file,
                      size: 20.0,
                    ),
                    const SizedBox(width: 10.0),
                    Expanded(
                      child: Text(
                        widget.fileName?.isNotEmpty == true
                            ? widget.fileName!
                            : widget.label,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: widget.fileName?.isNotEmpty == true
                              ? Colors.black
                              : Colors.black54,
                        ),
                      ),
                    ),
                    const SizedBox(width: 10.0),
                    const Icon(
                      Icons.folder_open,
                      size: 20.0,
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 15.0),
        ],
      ),
    );
  }
}