import 'package:bomcurriculo/view/Home.dart';
import 'package:bomcurriculo/widget/ButtonIcon.dart';
import 'package:flutter/material.dart';

class Navbar extends StatefulWidget {
  const Navbar({
    super.key,
    this.onMenuChanged
  });

  final VoidCallback? onMenuChanged;

  @override
  _Navbar createState() => _Navbar();
}

class _Navbar extends State<Navbar> {
  @override
  Widget build(BuildContext context) {
    return Container(
        width: double.infinity,
        height: 50.0,
        color: Color(0xFFEEEEEE),
        child: Row(
          children: [
            SizedBox(width: 11.0),
            Expanded(
                child: GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const Home(),
                      ),
                    );
                  },
                  child: Text(
                    'Bom Currículo',
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 18.0),
                  ),
                )
            ),
            (widget.onMenuChanged!=null)?GestureDetector(
              onTap: widget.onMenuChanged,
              child: ButtonIcon(icon: Icons.menu, color: Color(0xFFDDDDDD))
            ):SizedBox(),
            SizedBox(width: 5.0),
          ],
        )
    );
  }
}