#pragma once
#include <Arduino.h>

// Which card plays which folder on the SD card.
//
// To add a card: tap it, copy the ID the LCD (or Serial Monitor) shows into a new
// line below, pick its folder number (/01 = 1, /02 = 2, ...) and a title of up to
// 16 characters, then upload again.
//
// The table lives in flash (PROGMEM) so 30+ cards don't eat the Uno's 2KB of RAM.

struct Card {
  char uid[15];    // exactly as shown: "A3 4F 12 9C" or "04A1B2C3D4E5F6"
  uint8_t folder;  // 1-99, the SD card folder /01 .. /99
  char title[17];  // up to 16 characters, shown on LCD line 1
};

const Card CARDS[] PROGMEM = {
  // The Elegoo kit's white card and blue key fob, for testing.
  {"EB 5A 25 0B", 1, "Happy Tunes"},
  {"75 E2 5A D3", 2, "Bedtime"},
};

const uint8_t CARD_COUNT = sizeof(CARDS) / sizeof(CARDS[0]);
