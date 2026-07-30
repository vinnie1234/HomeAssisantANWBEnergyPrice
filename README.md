# ANWB Energy Price

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/vinnie1234/HomeAssisantANWBEnergyPrice)](https://github.com/vinnie1234/HomeAssisantANWBEnergyPrice/releases)

Haalt elk uur automatisch de actuele dynamische energieprijzen op van **ANWB Energie** en maakt ze beschikbaar als sensoren in Home Assistant.

De prijzen zijn gebaseerd op de dagelijkse spotmarktprijzen en worden door ANWB aangevuld met vaste kosten tot een all-in prijs. Handig voor automaties die apparaten sturen op het goedkoopste uur van de dag.

---

## Sensoren

De integratie maakt **10 sensoren** aan, verdeeld over twee categorieën:

### Marktprijs *(kale spotmarktprijs, excl. vaste kosten)*

| Sensor | Beschrijving | Icoon |
|---|---|---|
| `sensor.anwb_marktprijs_huidig` | Prijs van het huidige uur | ⚡ |
| `sensor.anwb_marktprijs_laagste_vandaag` | Laagste prijs van de dag | 📉 |
| `sensor.anwb_marktprijs_hoogste_vandaag` | Hoogste prijs van de dag | 📈 |
| `sensor.anwb_marktprijs_gemiddeld_vandaag` | Gemiddelde prijs van de dag | ≈ |
| `sensor.anwb_marktprijs_goedkoopste_uur_vandaag` | Goedkoopste uur van de dag + tijdstip | 🕐 |

### All-in prijs *(marktprijs + vaste kosten en belastingen)*

| Sensor | Beschrijving | Icoon |
|---|---|---|
| `sensor.anwb_allinprijs_huidig` | Prijs van het huidige uur | ⚡ |
| `sensor.anwb_allinprijs_laagste_vandaag` | Laagste prijs van de dag | 📉 |
| `sensor.anwb_allinprijs_hoogste_vandaag` | Hoogste prijs van de dag | 📈 |
| `sensor.anwb_allinprijs_gemiddeld_vandaag` | Gemiddelde prijs van de dag | ≈ |
| `sensor.anwb_allinprijs_goedkoopste_uur_vandaag` | Goedkoopste uur van de dag + tijdstip | 🕐 |

> Alle prijzen zijn in **ct/kWh** (eurocent per kilowattuur).

### Attributen

De sensoren `marktprijs_huidig` en `allinprijs_huidig` bevatten een attribuut `tarieven_per_uur` met alle uurprijzen van de dag. Handig om te gebruiken met [Apex Charts](https://github.com/RomRider/apexcharts-card) voor een grafiek.

De sensoren `goedkoopste_uur_vandaag` bevatten een attribuut `tijdstip` met het exacte uur waarop de laagste prijs geldt. Gebruik dit in automaties om bijvoorbeeld de wasmachine of het laden van een auto te starten.

---

## Installatie via HACS

1. Ga in Home Assistant naar **HACS → Integraties**
2. Klik op de drie puntjes (⋮) rechtsbovenin en kies **Aangepaste repositories**
3. Voeg deze URL toe: `https://github.com/vinnie1234/HomeAssisantANWBEnergyPrice`
4. Kies als categorie **Integratie** en klik op **Toevoegen**
5. Zoek op **ANWB Energy Price** en klik op **Downloaden**
6. Herstart Home Assistant
7. Ga naar **Instellingen → Apparaten & diensten → + Integratie toevoegen**
8. Zoek op **ANWB Energy** en volg de stappen

---

## Handmatige installatie

1. Download de map `custom_components/anwb_energy` uit deze repository
2. Kopieer de map naar de `custom_components` map in je Home Assistant configuratiemap
3. Herstart Home Assistant
4. Ga naar **Instellingen → Apparaten & diensten → + Integratie toevoegen**
5. Zoek op **ANWB Energy**

---

## Voorbeeld automatie — laad auto op goedkoopste uur

```yaml
alias: "Laad auto op goedkoopst uur"
trigger:
  - platform: time_pattern
    minutes: "0"
condition:
  - condition: template
    value_template: >
      {{ now().strftime('%Y-%m-%dT%H:00:00+00:00') ==
         state_attr('sensor.anwb_allinprijs_goedkoopste_uur_vandaag', 'tijdstip') }}
action:
  - service: switch.turn_on
    target:
      entity_id: switch.laadpaal
```

---

## Vernieuwen

De data wordt elk uur automatisch opgehaald. De API van ANWB publiceert de prijzen voor de volgende dag doorgaans rond 14:00 uur.

---

## Licentie

MIT
