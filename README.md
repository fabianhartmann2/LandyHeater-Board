# LandyHeater Board

Hardwareentwicklung für das Landy-Heater-Steuergerät auf Basis des `ESP32-S3-WROOM-1U-N16R8`.

## Aktueller Stand

Revision A befindet sich in der Schaltplan- und PCB-Designphase. Die verbindliche Grundlage für die Beauftragung und Prüfung des PCB-Designs ist aktuell Dokumentversion 1.4:

- [Hardware-Anforderungsspezifikation Revision A](docs/Hardware-Anforderungsspezifikation_Revision_A.md)

Die Spezifikation definiert Funktionsumfang, Schnittstellen, Versorgung, Mechanik, sichere Hardwarezustände, Layoutregeln, Fertigungsunterlagen und Abnahmetests. Die darin aufgeführten Verifikationspunkte müssen vor der Fertigungsfreigabe abgeschlossen werden.

## Abgrenzung Revision A

Revision A umfasst die AUTOTERM-UART-Schnittstelle, drei gemeinsam angeschlossene DS18B20-Sensoren, RTC, USB-C, externen Taster mit dimmbarer LED, eine lokale Energiefluss-Diagnoseanzeige sowie das Good-Display-E-Paper mit Touch und Frontlicht. VOTRONIC VBCS und Smart-Shunt sind für eine spätere Revision vorgemerkt.
