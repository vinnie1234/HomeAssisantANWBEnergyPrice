# ANWB Energy Price — Home Assistant integratie

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Haalt elk uur de actuele dynamische energieprijzen op van ANWB Energie en maakt ze beschikbaar als sensoren in Home Assistant.

## Sensoren

| Entiteit | Beschrijving |
|---|---|
| `sensor.anwb_marktprijs_huidig` | Huidige marktprijs (ct/kWh) — inclusief uurtarieven als attribuut |
| `sensor.anwb_allinprijs_huidig` | Huidige all-in prijs (ct/kWh) — inclusief uurtarieven als attribuut |
| `sensor.anwb_marktprijs_laagste_vandaag` | Laagste marktprijs van vandaag |
| `sensor.anwb_marktprijs_hoogste_vandaag` | Hoogste marktprijs van vandaag |
| `sensor.anwb_marktprijs_gemiddeld_vandaag` | Gemiddelde marktprijs van vandaag |
| `sensor.anwb_allinprijs_laagste_vandaag` | Laagste all-in prijs van vandaag |
| `sensor.anwb_allinprijs_hoogste_vandaag` | Hoogste all-in prijs van vandaag |
| `sensor.anwb_allinprijs_gemiddeld_vandaag` | Gemiddelde all-in prijs van vandaag |

De sensoren `marktprijs_huidig` en `allinprijs_huidig` bevatten een attribuut `tarieven_per_uur` met alle uurtarieven van de dag.

## Installatie via HACS

1. Voeg deze repository toe als **Custom repository** in HACS (`Integraties` → `⋮` → `Aangepaste repositories`)
2. Zoek op `ANWB Energy Price` en installeer
3. Herstart Home Assistant
4. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen** en zoek op `ANWB Energy`

## Handmatige installatie

Kopieer de map `custom_components/anwb_energy` naar de map `custom_components` in je Home Assistant configuratiemap.

## Licentie

MIT
