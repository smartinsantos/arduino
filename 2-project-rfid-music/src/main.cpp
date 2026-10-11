#include <Arduino.h>
#include <LiquidCrystal.h>
#include <MFRC522.h>
#include <SPI.h>

// RFID music box, phase 1: tap a card, see its ID on the LCD and in the Serial Monitor.
// Phase 2 will map those IDs to folders of songs on the MP3 player.

// RC522 reader on the Mega's hardware SPI pins (MOSI 51, MISO 50, SCK 52).
const int RFID_SS_PIN = 53;
const int RFID_RST_PIN = 49;

// LCD1602 in 4-bit parallel mode: RS, E, D4, D5, D6, D7.
const int LCD_RS = 7, LCD_E = 8, LCD_D4 = 9, LCD_D5 = 10, LCD_D6 = 11, LCD_D7 = 12;
const int LCD_COLS = 16;

const unsigned long SHOW_CARD_MS = 3000;  // how long a card's ID stays on screen

MFRC522 rfid(RFID_SS_PIN, RFID_RST_PIN);
LiquidCrystal lcd(LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

bool showingCard = false;
unsigned long cardShownAt = 0;

// "A3 4F 12 9C". A 7-byte UID would be 20 characters with spaces, too wide for
// the LCD, so it falls back to "04A1B2C3D4E5F6".
String formatUid(const MFRC522::Uid &uid) {
  bool spaced = uid.size * 3 - 1 <= LCD_COLS;
  String text;
  for (byte i = 0; i < uid.size; i++) {
    if (spaced && i > 0) text += ' ';
    if (uid.uidByte[i] < 0x10) text += '0';
    text += String(uid.uidByte[i], HEX);
  }
  text.toUpperCase();
  return text;
}

void showIdle() {
  lcd.clear();
  lcd.print("Tap a card...");
  showingCard = false;
}

void showCard(const String &uidText) {
  lcd.clear();
  lcd.print("Card:");
  lcd.setCursor(0, 1);
  lcd.print(uidText);
  showingCard = true;
  cardShownAt = millis();
}

void setup() {
  Serial.begin(9600);
  lcd.begin(LCD_COLS, 2);
  SPI.begin();
  rfid.PCD_Init();

  Serial.println("RFID music box - phase 1. Tap a card.");
  showIdle();
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uidText = formatUid(rfid.uid);
    showCard(uidText);
    Serial.print("Card UID: ");
    Serial.println(uidText);

    // Put the card to sleep so a card left on the reader is reported once, not every loop.
    rfid.PICC_HaltA();
  }

  if (showingCard && millis() - cardShownAt >= SHOW_CARD_MS) {
    showIdle();
  }
}
