import 'package:bomcurriculo/include/Navbar.dart';
import 'package:bomcurriculo/widget/Button.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class Home extends StatefulWidget {
  const Home({super.key});
  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  void doAction() {}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const Navbar(),
      body: SingleChildScrollView(
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
                          text: "Bem-vindo, ",
                          style: TextStyle(fontWeight: FontWeight(800)),
                        ),
                        TextSpan(
                          text: "Leonardo",
                          style: TextStyle(
                            color: Colors.blue,
                            fontWeight: FontWeight(800),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    "Seus Currículos otimizados em um só lugar.",
                    style: TextStyle(fontWeight: FontWeight(700)),
                  ),
                  SizedBox(
                    width: double.infinity,
                    child: Card(
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // ATS SCORE
                            Container(
                              width: 90,
                              height: 90,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: Colors.blue,
                                  width: 5,
                                ),
                              ),
                              child: const Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      "85",
                                      style: TextStyle(
                                        fontSize: 30,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    Text(
                                      "ATS SCORE",
                                      style: TextStyle(fontSize: 10),
                                    ),
                                  ],
                                ),
                              ),
                            ),

                            const SizedBox(width: 20),

                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.blue.shade50,
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                    child: const Text(
                                      "MÉDIA GLOBAL",
                                      style: TextStyle(
                                        color: Colors.blue,
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),

                                  const SizedBox(height: 8),

                                  const Text(
                                    "Performance Geral",
                                    style: TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),

                                  const SizedBox(height: 8),

                                  const Text(
                                    "Sua pontuação média de otimização está excelente.",
                                  ),

                                  const SizedBox(height: 4),

                                  const Text(
                                    "Foque em adicionar palavras-chave específicas para as vagas de Product Designer para atingir a nota máxima.",
                                  ),

                                  const SizedBox(height: 12),

                                  Wrap(
                                    spacing: 8,
                                    children: [
                                      Chip(
                                        label: Text("Keywords"),
                                        backgroundColor: Colors.blue.shade50,
                                      ),
                                      Chip(
                                        label: Text("Formatação"),
                                        backgroundColor: Colors.blue.shade50,
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 25),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        "Meus Currículos",
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      GestureDetector(
                        onTap: () {},
                        child: const Text(
                          "Ver todos",
                          style: TextStyle(
                            color: Colors.blue,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 15),

                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        Container(
                          width: 210,
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
                                    children: const [
                                      Text(
                                        "92",
                                        style: TextStyle(
                                          color: Colors.blue,
                                          fontSize: 26,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      Text(
                                        "ATS SCORE",
                                        style: TextStyle(fontSize: 10),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 15),
                              const Text(
                                "Currículo_ProductDesigner_v2.pdf",
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 5),
                              const Text(
                                "Atualizado há 2 dias",
                                style: TextStyle(color: Colors.grey),
                              ),
                              const SizedBox(height: 15),
                              Row(
                                children: const [
                                  Icon(Icons.language, size: 16),
                                  SizedBox(width: 5),
                                  Text("pt-BR"),
                                  Spacer(),
                                  Icon(Icons.more_vert),
                                ],
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(width: 15),

                        Container(
                          width: 210,
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
                                    children: const [
                                      Text(
                                        "78",
                                        style: TextStyle(
                                          color: Colors.blue,
                                          fontSize: 26,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      Text(
                                        "ATS SCORE",
                                        style: TextStyle(fontSize: 10),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 15),
                              const Text(
                                "Currículo_MarketingDigital.pdf",
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 5),
                              const Text(
                                "Atualizado há 1 semana",
                                style: TextStyle(color: Colors.grey),
                              ),
                              const SizedBox(height: 15),
                              Row(
                                children: const [
                                  Icon(Icons.language, size: 16),
                                  SizedBox(width: 5),
                                  Text("pt-BR"),
                                  Spacer(),
                                  Icon(Icons.more_vert),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 50.0),
                  Container(),
                  GestureDetector(
                    onTap: () {
                      context.go('/auth/login');
                    },
                    child: Button(title: 'Login'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
