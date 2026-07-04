import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class WidgetInputText extends StatefulWidget {
  const WidgetInputText({
    super.key,
    this.isPassword = false,
    this.title = '',
    this.label = '',
    this.httpsPrefix = '',
    this.controller,
    this.previousController,
    this.focusNode,
    this.nextFocusNode,
    this.previousFocusNode,
    this.maxLength,
    this.textAlignCenter = false,
    this.error = ''
  });

  final bool isPassword;
  final String? title;
  final String? label;
  final String? httpsPrefix;
  final TextEditingController? controller;
  final TextEditingController? previousController;

  final FocusNode? focusNode;
  final FocusNode? previousFocusNode;
  final FocusNode? nextFocusNode;
  final int? maxLength;

  final bool textAlignCenter;

  final String? error;

  @override
  _WidgetInputText createState() => _WidgetInputText();
}

class _WidgetInputText extends State<WidgetInputText> {
  late final FocusNode _focusNode = widget.focusNode ?? FocusNode();

  // controla se o campo já estava vazio ANTES do backspace ser apertado,
  // pra decidir se quem trata o "voltar" é o onKeyEvent ou o onChanged
  bool _wasEmptyBeforeKey = false;

  @override
  void initState() {
    super.initState();
    _focusNode.onKeyEvent = _handleKeyEvent;
  }

  @override
  void dispose() {
    _focusNode.onKeyEvent = null;
    if (widget.focusNode == null) {
      _focusNode.dispose();
    }
    super.dispose();
  }

  KeyEventResult _handleKeyEvent(FocusNode node, KeyEvent event) {

    if (widget.maxLength != 1) {
      return KeyEventResult.ignored;
    }

    final isBackspace = event.logicalKey == LogicalKeyboardKey.backspace;
    if (!isBackspace) return KeyEventResult.ignored;

    if (event is KeyDownEvent) {
      final isEmpty = widget.controller?.text.isEmpty ?? true;
      _wasEmptyBeforeKey = isEmpty;

      // se o campo JÁ estava vazio antes desse backspace, volta na hora.
      // se não estava vazio, deixa o backspace apagar o dígito primeiro
      // (o onChanged vai cuidar de voltar o foco)
      if (isEmpty) {
        _focusPreviousAndSelectEnd();
        return KeyEventResult.handled;
      }
    }

    return KeyEventResult.ignored;
  }

  void _focusPreviousAndSelectEnd() {
    final previousFocus = widget.previousFocusNode;
    final previousController = widget.previousController;

    if (previousFocus == null) return;

    previousFocus.requestFocus();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (previousController != null) {
        previousController.selection = TextSelection.fromPosition(
          TextPosition(offset: previousController.text.length),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if ((widget.title ?? '').isNotEmpty) ...[
            Text(widget.title!, style: const TextStyle(fontSize: 16.0)),
            const SizedBox(height: 5.0),
          ],
          Container(
            decoration: BoxDecoration(
              color: const Color(0xFFEEEEEE),
              borderRadius: BorderRadius.circular(4.0),
            ),
            child: TextField(
              controller: widget.controller,
              focusNode: _focusNode,
              maxLength: widget.maxLength,
              keyboardType: widget.maxLength == 1 ? TextInputType.number : TextInputType.text,
              inputFormatters: widget.maxLength == 1 ? [FilteringTextInputFormatter.digitsOnly] : null,
              textAlign:
                  widget.textAlignCenter ? TextAlign.center : TextAlign.start,
              obscureText: widget.isPassword,
              onChanged: (value) {
                if (widget.maxLength != 1) return;

                if (value.length == 1) {
                  widget.nextFocusNode?.requestFocus();
                } else if (value.isEmpty && !_wasEmptyBeforeKey) {
                  // o backspace acabou de apagar o dígito que tinha
                  // (o campo NÃO estava vazio antes) -> volta já
                  _focusPreviousAndSelectEnd();
                }
              },
              decoration: InputDecoration(
                prefixText: widget.httpsPrefix,
                counterText: "",
                isDense: true,
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12.0,
                  vertical: 12.0,
                ),
              ),
            ),
          ),

          SizedBox(height: widget.error!=""?5.0:0),
          widget.error!=""?Text(widget.error!, style: TextStyle(color: Colors.red)):SizedBox(),

          const SizedBox(height: 15.0),
        ],
      ),
    );
  }
}