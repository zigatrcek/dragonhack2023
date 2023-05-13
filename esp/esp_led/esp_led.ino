void setup() {
  Serial.begin(115200);
}
void loop() {
 
  while(Serial.available()){
    Serial.write(Serial.read());
  }
  delay(10);
}