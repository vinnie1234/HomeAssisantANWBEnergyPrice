# ANWB Energy Price

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/vinnie1234/HomeAssisantANWBEnergyPrice)](https://github.com/vinnie1234/HomeAssisantANWBEnergyPrice/releases)

Automatically fetches dynamic electricity and gas prices from **ANWB Energie** every hour and exposes them as sensors in Home Assistant.

Prices are based on the daily spot market and supplemented by ANWB with fixed costs to produce an all-in price. Useful for automations that schedule appliances to run at the cheapest hour of the day.

---

## Sensors

The integration creates **20 sensors** — 10 for electricity and 10 for gas.

### Electricity

| Sensor | Description | Icon |
|---|---|---|
| `sensor.anwb_electricity_market_price_current` | Market price for the current hour | ⚡ |
| `sensor.anwb_electricity_all_in_price_current` | All-in price for the current hour | ⚡ |
| `sensor.anwb_electricity_market_price_lowest_today` | Lowest market price of the day | 📉 |
| `sensor.anwb_electricity_market_price_highest_today` | Highest market price of the day | 📈 |
| `sensor.anwb_electricity_market_price_average_today` | Average market price of the day | ≈ |
| `sensor.anwb_electricity_all_in_price_lowest_today` | Lowest all-in price of the day | 📉 |
| `sensor.anwb_electricity_all_in_price_highest_today` | Highest all-in price of the day | 📈 |
| `sensor.anwb_electricity_all_in_price_average_today` | Average all-in price of the day | ≈ |
| `sensor.anwb_electricity_market_price_cheapest_hour` | Cheapest market price hour + timestamp | 🕐 |
| `sensor.anwb_electricity_all_in_price_cheapest_hour` | Cheapest all-in price hour + timestamp | 🕐 |

### Gas

| Sensor | Description | Icon |
|---|---|---|
| `sensor.anwb_gas_market_price_current` | Market price for the current hour | 🔥 |
| `sensor.anwb_gas_all_in_price_current` | All-in price for the current hour | 🔥 |
| `sensor.anwb_gas_market_price_lowest_today` | Lowest market price of the day | 📉 |
| `sensor.anwb_gas_market_price_highest_today` | Highest market price of the day | 📈 |
| `sensor.anwb_gas_market_price_average_today` | Average market price of the day | ≈ |
| `sensor.anwb_gas_all_in_price_lowest_today` | Lowest all-in price of the day | 📉 |
| `sensor.anwb_gas_all_in_price_highest_today` | Highest all-in price of the day | 📈 |
| `sensor.anwb_gas_all_in_price_average_today` | Average all-in price of the day | ≈ |
| `sensor.anwb_gas_market_price_cheapest_hour` | Cheapest market price hour + timestamp | 🕐 |
| `sensor.anwb_gas_all_in_price_cheapest_hour` | Cheapest all-in price hour + timestamp | 🕐 |

> All prices are in **ct/kWh** (euro cents per kilowatt-hour).

### Attributes

The `*_current` sensors expose an `hourly_prices` attribute containing all hourly prices for the day. Useful with [Apex Charts](https://github.com/RomRider/apexcharts-card) to display a price graph.

The `cheapest_hour` sensors expose a `time` attribute with the exact hour at which the lowest price occurs. Use this in automations to start the washing machine or charge an EV at the right moment.

---

## Installation via HACS

1. Go to **HACS → Integrations** in Home Assistant
2. Click the three dots (⋮) in the top right and choose **Custom repositories**
3. Add this URL: `https://github.com/vinnie1234/HomeAssisantANWBEnergyPrice`
4. Select **Integration** as the category and click **Add**
5. Search for **ANWB Energy Price** and click **Download**
6. Restart Home Assistant
7. Go to **Settings → Devices & Services → + Add Integration**
8. Search for **ANWB Energy** and follow the steps

---

## Manual installation

1. Download the `custom_components/anwb_energy` folder from this repository
2. Copy it into the `custom_components` folder in your Home Assistant configuration directory
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → + Add Integration**
5. Search for **ANWB Energy**

---

## Example automation — charge EV at the cheapest hour

```yaml
alias: "Charge EV at cheapest hour"
trigger:
  - platform: time_pattern
    minutes: "0"
condition:
  - condition: template
    value_template: >
      {{ now().strftime('%Y-%m-%dT%H:00:00+00:00') ==
         state_attr('sensor.anwb_electricity_all_in_price_cheapest_hour', 'time') }}
action:
  - service: switch.turn_on
    target:
      entity_id: switch.ev_charger
```

---

## Data refresh

Data is fetched automatically every hour. The ANWB API typically publishes the next day's electricity prices around 14:00 local time. Gas prices update less frequently and may stay the same for multiple hours.

---

## License

MIT
