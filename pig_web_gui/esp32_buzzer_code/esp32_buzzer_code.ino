#define BUZZER 25
#define LED 26

bool alarmOn = false;

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER, OUTPUT);
  pinMode(LED, OUTPUT);
}

void loop() {

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "1") {
      alarmOn = true;
      Serial.println("ON");
    }

    if (cmd == "0") {
      alarmOn = false;
      noTone(BUZZER);
      digitalWrite(LED, LOW);
      Serial.println("OFF");
    }
  }

  if (alarmOn) {
    digitalWrite(LED,HIGH);
    for (int f = 2000; f <= 5000; f += 300) {
      // int brightness = map(f, 2000, 5000, 0, 255);
      // analogWrite(LED, brightness);
      tone(BUZZER, f);
      delay(80);
    }

    for (int f = 5000; f >= 2000; f -= 300) {
      // int brightness = map(f, 2000, 5000, 0, 255);
      // analogWrite(LED, brightness);
      tone(BUZZER, f);
      delay(30);
    }
  }
}


// #define BUZZER 13

// void setup() {

//   Serial.begin(115200);

//   pinMode(BUZZER, OUTPUT);

// }

// void loop() {

//   if (Serial.available()) {

//     String cmd = Serial.readStringUntil('\n');

//     cmd.trim();

//     Serial.print("Received: ");
//     Serial.println(cmd);

//     if (cmd == "1") {

//       Serial.println("BUZZER ON");

//       tone(BUZZER, 1000);

//     }

//     else if (cmd == "0") {

//       Serial.println("BUZZER OFF");

//       noTone(BUZZER);

//       digitalWrite(BUZZER, LOW);

//     }
//   }
// }