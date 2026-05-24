import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent
ROW_COUNT = 1000
POLYGON_IDS = (1, 2, 3)
START_DT = datetime(2025, 1, 1, 0, 0, 0)
MISSING_PROBABILITY = 0.015

HEADERS = [
    "Дата",
    "CO2",
    "Влажность",
    "Температура",
    "Давление",
    "Освещённость",
    "Уровень шума",
]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _maybe_blank(value: str) -> str:
    return "" if random.random() < MISSING_PROBABILITY else value


def _generate_row(index: int, polygon_shift: float) -> list[str]:
    dt = START_DT + timedelta(hours=index)
    hour = dt.hour + dt.minute / 60
    day_wave = math.sin((2 * math.pi / 24) * hour)
    week_wave = math.sin((2 * math.pi / (24 * 7)) * index)

    co2 = _clamp(520 + 140 * day_wave + 90 * week_wave + random.uniform(-40, 40) + polygon_shift * 10, 380, 900)
    humidity = _clamp(58 - 15 * day_wave + 8 * week_wave + random.uniform(-5, 5) + polygon_shift, 30, 90)
    temperature = _clamp(14 + 11 * day_wave + 7 * week_wave + random.uniform(-2, 2) + polygon_shift * 0.8, -10, 35)
    pressure = _clamp(1008 + 6 * week_wave + random.uniform(-3.5, 3.5) + polygon_shift * 0.7, 970, 1040)

    if 7 <= dt.hour <= 20:
        light_base = 700 * max(0, math.sin(math.pi * (dt.hour - 7) / 13))
    else:
        light_base = 0
    light = _clamp(light_base + random.uniform(-70, 70) + polygon_shift * 20, 0, 1000)

    noise = _clamp(38 + 18 * max(day_wave, 0) + random.uniform(-6, 6) + polygon_shift * 1.5, 20, 90)

    return [
        dt.strftime("%Y-%m-%d %H:%M:%S"),
        _maybe_blank(str(round(co2))),
        _maybe_blank(str(round(humidity))),
        _maybe_blank(f"{temperature:.1f}"),
        _maybe_blank(str(round(pressure))),
        _maybe_blank(str(round(light))),
        _maybe_blank(str(round(noise))),
    ]


def generate() -> None:
    random.seed(42)
    for polygon_id in POLYGON_IDS:
        file_name = f"polygon_{polygon_id}_measurements.csv"
        file_path = OUTPUT_DIR / file_name
        polygon_shift = float(polygon_id - 2)

        with file_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(HEADERS)
            for i in range(ROW_COUNT):
                writer.writerow(_generate_row(i, polygon_shift))

        print(f"Generated: {file_path}")


if __name__ == "__main__":
    generate()
