import 'package:flutter/material.dart';

/// Tema claro
class AppColorsLight {
  AppColorsLight._();

  // Marca
  static const Color brandPrimary = Color(0xFF2E7BFF);
  static const Color brandPrimaryForeground = Color(0xFFFFFFFF);
  static const Color brandPrimaryTint = Color(0xFFDCE1FF);

  static const Color brandSecondary = Color(0xFF03206E);
  static const Color brandSecondaryForeground = Color(0xFFFFFFFF);

  // Base
  static const Color background = Color(0xFFFFFFFF);
  static const Color foreground = Color(0xFF171717);

  static const Color card = Color(0xFFFFFFFF);
  static const Color cardForeground = foreground;

  static const Color popover = Color(0xFFFFFFFF);
  static const Color popoverForeground = foreground;

  static const Color primary = Color(0xFF343434);
  static const Color primaryForeground = Color(0xFFFFFFFF);

  static const Color secondary = Color(0xFFF5F5F5);
  static const Color secondaryForeground = foreground;

  static const Color muted = Color(0xFFF5F5F5);
  static const Color mutedForeground = Color(0xFF737373);

  static const Color accent = Color(0xFFF5F5F5);
  static const Color accentForeground = foreground;

  static const Color destructive = Color(0xFFE11D48);

  static const Color border = Color(0xFFE5E5E5);
  static const Color input = border;
  static const Color ring = Color(0xFFA3A3A3);

  // Sidebar
  static const Color sidebar = Color(0xFFFCFCFC);
  static const Color sidebarForeground = foreground;
  static const Color sidebarPrimary = primary;
  static const Color sidebarPrimaryForeground = Color(0xFFFFFFFF);
  static const Color sidebarAccent = secondary;
  static const Color sidebarAccentForeground = foreground;
  static const Color sidebarBorder = border;
  static const Color sidebarRing = ring;

  // Charts
  static const Color chart1 = Color(0xFFDEDEDE);
  static const Color chart2 = Color(0xFF737373);
  static const Color chart3 = Color(0xFF525252);
  static const Color chart4 = Color(0xFF404040);
  static const Color chart5 = Color(0xFF262626);
  static const Color chartGrid = Color(0xFFE5E7EB);

  static const Color inputBorderStrong = foreground;
}

/// Tema escuro
class AppColorsDark {
  AppColorsDark._();

  // Marca (não muda)
  static const Color brandPrimary = Color(0xFF2E7BFF);
  static const Color brandPrimaryForeground = Color(0xFFFFFFFF);
  static const Color brandPrimaryTint = Color(0xFFDCE1FF);

  static const Color brandSecondary = Color(0xFF03206E);
  static const Color brandSecondaryForeground = Color(0xFFFFFFFF);

  // Base
  static const Color background = Color(0xFF171717);
  static const Color foreground = Color(0xFFFAFAFA);

  static const Color card = Color(0xFF343434);
  static const Color cardForeground = foreground;

  static const Color popover = Color(0xFF343434);
  static const Color popoverForeground = foreground;

  static const Color primary = Color(0xFFE5E5E5);
  static const Color primaryForeground = Color(0xFF343434);

  static const Color secondary = Color(0xFF262626);
  static const Color secondaryForeground = foreground;

  static const Color muted = Color(0xFF262626);
  static const Color mutedForeground = Color(0xFFA3A3A3);

  static const Color accent = Color(0xFF262626);
  static const Color accentForeground = foreground;

  static const Color destructive = Color(0xFFFB7185);

  static const Color border = Color(0x1AFFFFFF);
  static const Color input = Color(0x26FFFFFF);
  static const Color ring = Color(0xFF737373);

  // Sidebar
  static const Color sidebar = Color(0xFF343434);
  static const Color sidebarForeground = foreground;
  static const Color sidebarPrimary = Color(0xFF4F46E5);
  static const Color sidebarPrimaryForeground = Color(0xFFFAFAFA);
  static const Color sidebarAccent = secondary;
  static const Color sidebarAccentForeground = foreground;
  static const Color sidebarBorder = Color(0x1AFFFFFF);
  static const Color sidebarRing = ring;

  // Charts
  static const Color chart1 = Color(0xFFDEDEDE);
  static const Color chart2 = Color(0xFF737373);
  static const Color chart3 = Color(0xFF525252);
  static const Color chart4 = Color(0xFF404040);
  static const Color chart5 = Color(0xFF262626);
  static const Color chartGrid = Color(0xFFE5E7EB);

  static const Color inputBorderStrong = foreground;
}
