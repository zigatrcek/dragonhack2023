void setup() {
  Serial.begin(115200);
}
void loop() {
  while(Serial.available()){
    int read = Serial.read();
    Serial.println(read);
    Serial.write(read);
  }
  delay(10);
}