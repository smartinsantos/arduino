#include <Arduino.h>
#include <DFRobotDFPlayerMini.h>
#include <LiquidCrystal.h>
#include <MFRC522.h>
#include <SPI.h>
#include <SoftwareSerial.h>

#include "cards.h"

// RFID music box, phase 2: tap a card and the songs in its SD card folder play in
// order. A knob sets the volume; three buttons do previous, play/pause and next.
// Unknown cards show their ID so they can be added to cards.h.

// RC522 reader on the Uno's hardware SPI pins (MOSI 11, MISO 12, SCK 13).
const int RFID_SS_PIN = 10;
const int RFID_RST_PIN = 9;

// LCD1602 in 4-bit parallel mode: RS, E, D4, D5, D6, D7.
const int LCD_RS = 2, LCD_E = 3, LCD_D4 = 4, LCD_D5 = 5, LCD_D6 = 6, LCD_D7 = 7;
const int LCD_COLS = 16;

// DFPlayer Mini on SoftwareSerial, so the hardware Serial stays free for USB.
const int MP3_RX_PIN = 8;     // Uno receives on D8  <- DFPlayer TX
const int MP3_TX_PIN = A1;    // Uno sends on A1 -> 1k ohm -> DFPlayer RX
const int MP3_BUSY_PIN = A2;  // LOW while a song is playing

// Volume knob (potentiometer middle leg) and buttons (pin to GND, pressed = LOW).
const int VOLUME_PIN = A0;
const int PREV_PIN = A3;
const int PLAY_PAUSE_PIN = A4;
const int NEXT_PIN = A5;

const uint8_t MAX_VOLUME = 30;  // full turn of the knob = the module's maximum

const unsigned long NEW_CARD_MS = 3000;    // how long an unknown card's ID stays on screen
const unsigned long BUSY_GRACE_MS = 1000;  // BUSY needs a moment to go LOW after a play command
const unsigned long KNOB_READ_MS = 100;    // read the knob about 10 times a second
const int KNOB_DEADBAND = 24;              // ignore knob jitter smaller than this (of 1023), half a volume step
const unsigned long DEBOUNCE_MS = 30;

MFRC522 rfid(RFID_SS_PIN, RFID_RST_PIN);
LiquidCrystal lcd(LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7);
SoftwareSerial mp3Serial(MP3_RX_PIN, MP3_TX_PIN);
DFRobotDFPlayerMini player;

enum Mode : uint8_t {
  NO_CARD,   // power on, no known card tapped yet
  PLAYING,
  PAUSED,
  FINISHED,  // the folder played to the end
};

Mode mode = NO_CARD;
Card current;        // the card whose folder is playing (or last played)
int songNumber = 0;  // 1-based
int songCount = 0;   // 0 = not known yet; learned when the module reports the next song missing
bool skipping = false;  // the current song was started by the Next button
unsigned long songStartedAt = 0;

bool showingNewCard = false;
unsigned long newCardShownAt = 0;

uint8_t volume = 0;
int knobRaw = -1000;  // knob reading the volume was last set from
unsigned long knobReadAt = 0;

struct Button {
  int pin;
  bool pressed;  // debounced state
  bool lastReading;
  unsigned long changedAt;
};

Button prevButton = {PREV_PIN, false, false, 0};
Button playPauseButton = {PLAY_PAUSE_PIN, false, false, 0};
Button nextButton = {NEXT_PIN, false, false, 0};

// "A3 4F 12 9C". A 7-byte UID would be 20 characters with spaces, too wide for
// the LCD, so it falls back to "04A1B2C3D4E5F6". `out` needs room for 21 chars.
void formatUid(const MFRC522::Uid &uid, char *out) {
  const char HEX_DIGITS[] = "0123456789ABCDEF";
  bool spaced = uid.size * 3 - 1 <= LCD_COLS;
  char *p = out;
  for (byte i = 0; i < uid.size; i++) {
    if (spaced && i > 0) *p++ = ' ';
    *p++ = HEX_DIGITS[uid.uidByte[i] >> 4];
    *p++ = HEX_DIGITS[uid.uidByte[i] & 0x0F];
  }
  *p = '\0';
}

// Copies the matching card out of flash into `found`. False if the ID isn't in cards.h.
bool findCard(const char *uidText, Card &found) {
  for (uint8_t i = 0; i < CARD_COUNT; i++) {
    memcpy_P(&found, &CARDS[i], sizeof(Card));
    if (strcmp(found.uid, uidText) == 0) return true;
  }
  return false;
}

void halt(const __FlashStringHelper *line1, const __FlashStringHelper *line2) {
  lcd.clear();
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
  while (true) {}
}

// ---------- screen ----------

// What the screen shows when nothing temporary is on it.
void showStatus() {
  if (showingNewCard) return;
  lcd.clear();
  if (mode != PLAYING && mode != PAUSED) {
    lcd.print(F("Tap a card..."));
    return;
  }
  lcd.print(current.title);
  lcd.setCursor(0, 1);
  lcd.print(mode == PAUSED ? F("Paused  ") : F("Song "));
  lcd.print(songNumber);
}

void showNewCard(const char *uidText) {
  lcd.clear();
  lcd.print(F("New card:"));
  lcd.setCursor(0, 1);
  lcd.print(uidText);
  showingNewCard = true;
  newCardShownAt = millis();
}

// ---------- playback ----------

void playSong(int number) {
  songNumber = number;
  player.playFolder(current.folder, songNumber);
  songStartedAt = millis();
  mode = PLAYING;
  Serial.print(F("Playing folder "));
  Serial.print(current.folder);
  Serial.print(F(" song "));
  Serial.println(songNumber);
  showStatus();
}

void startFolder(const Card &card) {
  current = card;
  skipping = false;
  // Don't ask the module how many songs the folder has: clone DFPlayers answer that
  // query (0x4E) with an error, and the library then returns a stale reply instead.
  // Play on until the module reports "file not found" (see handlePlayer).
  songCount = 0;
  playSong(1);
}

void finishFolder() {
  mode = FINISHED;
  Serial.println(F("Folder finished"));
  showStatus();
}

void nextSong() {
  if (songCount > 0 && songNumber >= songCount) {
    skipping = false;
    playSong(1);  // wrap around
  } else {
    skipping = true;
    playSong(songNumber + 1);
  }
}

void previousSong() {
  skipping = false;
  playSong(songNumber > 1 ? songNumber - 1 : 1);
}

void togglePause() {
  if (mode == PLAYING) {
    player.pause();
    mode = PAUSED;
    Serial.println(F("Paused"));
  } else if (mode == PAUSED) {
    player.start();
    songStartedAt = millis();  // BUSY needs a moment to go LOW again
    mode = PLAYING;
    Serial.println(F("Resumed"));
  } else if (mode == FINISHED) {
    startFolder(current);
    return;
  }
  showStatus();
}

// ---------- inputs ----------

void handleCard() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  char uidText[21];
  formatUid(rfid.uid, uidText);
  Serial.print(F("Card UID: "));
  Serial.println(uidText);

  // Put the card to sleep so a card left on the reader is reported once, not every loop.
  rfid.PICC_HaltA();

  // Only a change of card does anything. Re-tapping the current card is ignored.
  if (mode != NO_CARD && strcmp(uidText, current.uid) == 0) return;

  Card card;
  if (findCard(uidText, card)) {
    showingNewCard = false;
    startFolder(card);
  } else {
    // Unknown card: show its ID, keep the music going, and don't make it the current card.
    showNewCard(uidText);
  }
}

// True once per press, after the reading has been steady for DEBOUNCE_MS.
bool wasPressed(Button &button) {
  bool reading = digitalRead(button.pin) == LOW;
  if (reading != button.lastReading) {
    button.lastReading = reading;
    button.changedAt = millis();
  }
  if (millis() - button.changedAt < DEBOUNCE_MS || reading == button.pressed) return false;
  button.pressed = reading;
  return reading;
}

void handleButtons() {
  // Read all three every loop so their debounce timers keep running.
  bool prev = wasPressed(prevButton);
  bool playPause = wasPressed(playPauseButton);
  bool next = wasPressed(nextButton);

  if (playPause && mode != NO_CARD) togglePause();
  // Next and previous work while playing or paused (and start playing); ignored otherwise.
  if (mode != PLAYING && mode != PAUSED) return;
  if (next) nextSong();
  if (prev) previousSong();
}

void handleKnob(bool force) {
  if (!force && millis() - knobReadAt < KNOB_READ_MS) return;
  knobReadAt = millis();

  int raw = 0;
  for (int i = 0; i < 4; i++) raw += analogRead(VOLUME_PIN);  // average out electrical noise
  raw /= 4;
  if (!force && abs(raw - knobRaw) < KNOB_DEADBAND) return;
  knobRaw = raw;

  uint8_t newVolume = (long)raw * (MAX_VOLUME + 1) / 1024;  // 0..MAX_VOLUME
  if (!force && newVolume == volume) return;
  volume = newVolume;
  player.volume(volume);
  Serial.print(F("Volume "));
  Serial.println(volume);
}

void handlePlayer() {
  if (mode != PLAYING) return;

  // "File not found" for the song we just asked for: the folder has no more songs.
  if (player.available() && player.readType() == DFPlayerError && player.read() == FileMismatch) {
    songCount = songNumber - 1;
    if (skipping && songCount > 0) {
      skipping = false;
      playSong(1);  // Next on the last song wraps around
    } else {
      finishFolder();
    }
    return;
  }

  bool songEnded = millis() - songStartedAt >= BUSY_GRACE_MS && digitalRead(MP3_BUSY_PIN) == HIGH;
  if (!songEnded) return;

  skipping = false;
  if (songCount > 0 && songNumber >= songCount) {
    finishFolder();
  } else {
    playSong(songNumber + 1);
  }
}

void setup() {
  Serial.begin(9600);
  lcd.begin(LCD_COLS, 2);
  SPI.begin();
  rfid.PCD_Init();
  pinMode(MP3_BUSY_PIN, INPUT);
  pinMode(PREV_PIN, INPUT_PULLUP);
  pinMode(PLAY_PAUSE_PIN, INPUT_PULLUP);
  pinMode(NEXT_PIN, INPUT_PULLUP);

  Serial.println(F("RFID music box - phase 2."));
  lcd.print(F("Starting..."));

  // A missing or miswired reader answers 0x00 or 0xFF instead of a chip version.
  byte version = rfid.PCD_ReadRegister(MFRC522::VersionReg);
  if (version == 0x00 || version == 0xFF) {
    Serial.println(F("RC522 not found - check its wiring and 3.3V."));
    halt(F("RFID not found"), F("Check wiring"));
  }

  // begin() also fails when there is no SD card in the module.
  mp3Serial.begin(9600);
  if (!player.begin(mp3Serial, true, true)) {
    Serial.println(F("DFPlayer not found - check its wiring, the 1k resistor and the SD card."));
    halt(F("MP3 not found"), F("Check SD+wiring"));
  }
  player.setTimeOut(500);
  handleKnob(true);

  Serial.println(F("Ready. Tap a card."));
  showStatus();
}

void loop() {
  handleCard();
  handleButtons();
  handleKnob(false);
  handlePlayer();

  if (showingNewCard && millis() - newCardShownAt >= NEW_CARD_MS) {
    showingNewCard = false;
    showStatus();
  }
}
