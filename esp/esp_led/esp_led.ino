#include <Adafruit_NeoPixel.h>

#define LED_PIN 13
#define LED_NUM 29

Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUM, LED_PIN, NEO_GRBW + NEO_KHZ800);

void setup() {
  strip.begin();
  strip.show();
  Serial.begin(115200);
}

void loop() {
  while (Serial.available()) {
    int input = Serial.read();

    if (input == '0' || input = 0) {
      turnOff();
    } else if (input == '1' || input == 1) {
      turnOff();
      yellow();
    } else if (input == '2' || input == 2) {
      turnOff();
      blue();
    } else if (input == '3' || input == 3) {
      turnOff();
      white();
    } else if (input == '\n') {

    } else {
      Serial.println("jebote");
    }
    strip.show();
  }
  delay(10);
}

void turnOff() {
  uint32_t turnOff = strip.Color(0, 0, 0, 0);
  strip.fill(turnOff, 0, 29);
}

void yellow() {
  uint32_t yellow = strip.Color(255, 255, 0, 0);
  strip.fill(yellow, 0, 9);
}

void blue() {
  uint32_t blue = strip.Color(0, 0, 205, 0);
  strip.fill(blue, 9, 10);
}

void white() {
  uint32_t white = strip.Color(0, 0, 0, 255);
  strip.fill(white, 19, 10);
}
