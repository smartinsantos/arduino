#include <Arduino.h>

// Mini piano: 4 buttons, each plays a note and lights its own LED.
// C-D-E-G is a pentatonic scale, so any combination of presses sounds fine.

const int BUZZER_PIN = 6;

const int NUM_KEYS = 4;
const int BUTTON_PINS[NUM_KEYS] = {2, 3, 4, 5};
const int LED_PINS[NUM_KEYS] = {8, 9, 10, 11};
const int NOTES_HZ[NUM_KEYS] = {262, 294, 330, 392};  // C4, D4, E4, G4

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  for (int i = 0; i < NUM_KEYS; i++) {
    pinMode(BUTTON_PINS[i], INPUT_PULLUP);  // pressed = LOW
    pinMode(LED_PINS[i], OUTPUT);
  }
}

void loop() {
  int playing = -1;

  for (int i = 0; i < NUM_KEYS; i++) {
    bool pressed = digitalRead(BUTTON_PINS[i]) == LOW;
    digitalWrite(LED_PINS[i], pressed ? HIGH : LOW);
    if (pressed && playing == -1) {
      playing = i;  // first pressed key wins the speaker
    }
  }

  if (playing == -1) {
    noTone(BUZZER_PIN);
  } else {
    tone(BUZZER_PIN, NOTES_HZ[playing]);
  }
}
