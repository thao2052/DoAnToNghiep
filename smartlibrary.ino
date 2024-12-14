#include <Servo.h>
#include <LiquidCrystal_I2C.h>

#define servo1Pin 11
#define servo2Pin 10
#define servo3Pin 9
#define servo4Pin 6
#define servo5Pin 5
#define servo6Pin 3
#define relayPin  12

#define minUs  500
#define maxUs  2400

LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C address 0x27, 16 column and 2 rows
int sensorPin[] = {A0, A1, A2, A3, A6, A7};  // Các chân A0, A1, A2, A3, A6, A7
int sensorValue[6];  // Mảng lưu giá trị đọc từ các cảm biến

Servo servo1;
Servo servo2; 
Servo servo3; 
Servo servo4;  
Servo servo5; 
Servo servo6;  

int pos = 0;     
const int ledPin = 13; 
unsigned long relayStartTime = 0; // To track when the relay was turned on
bool relayOn = false;             // To track the state of the relay

void setup() {
  servo1.attach(servo1Pin, minUs, maxUs);
  servo2.attach(servo2Pin, minUs, maxUs);
  servo3.attach(servo3Pin, minUs, maxUs);
  servo4.attach(servo4Pin, minUs, maxUs);
  servo5.attach(servo5Pin, minUs, maxUs);
  servo6.attach(servo6Pin, minUs, maxUs);
  for (int i =0; i <6; i++)
  {
    pinMode(sensorPin[i], OUTPUT);
  }

  pinMode(relayPin, OUTPUT);
  pinMode(ledPin, OUTPUT);      
  digitalWrite(ledPin, LOW);    
  digitalWrite(relayPin, LOW);  // Ensure relay is off initially
  Serial.begin(9600);         
  lcd.init(); // initialize the lcd
  lcd.backlight();
  lcd.clear();                 // clear display
  lcd.setCursor(0, 0);         // move cursor to   (0, 0)
  lcd.print("  Smart Library ");        // print message at (0, 0)  
}

void loop() {
  for (int i = 0; i< 6; i++)
  {
    sensorValue[i] = digitalRead(sensorPin[i]);
    delay(10);
  }

  // Check for Serial input
  if (Serial.available() > 0) {
    String data_rcvd = Serial.readStringUntil('\n');
  Serial.println(data_rcvd);
   if (data_rcvd == "c#") {
    // if (0 == sensorValue[0])
    // {
      getBook1();
    // }
  } else if (data_rcvd == "csdl") {
    // if (!sensorValue[1])
    // {
      getBook2();
    // }
  } else if (data_rcvd == "ktmt") {
    // if (!sensorValue[2])
    // {
      getBook3();
    // }
  } else if (data_rcvd == "logic") {
    // if (!sensorValue[3])
    // {
      getBook4();
    // }
  } else if (data_rcvd == "Mac1") {
    // if (!sensorValue[4])
    // {
      getBook5();
    // }
  } else if (data_rcvd == "Mac2") {
    // if (sensorValue[5] == 0)
    // {
      getBook6();
    // }
  } else {
    Serial.println("Invalid input! Please send one of the valid commands.");
  }
  //    if (data_rcvd == "1") {
  //   getBook1();
  // } else if (data_rcvd == "2") {
  //   getBook2();
  // } else if (data_rcvd == "3") {
  //   getBook3();
  // } else if (data_rcvd == "4") {
  //   getBook4();
  // } else if (data_rcvd == "5") {
  //   getBook5();
  // } else if (data_rcvd == "6") {
  //   getBook6();
  // } else {
  //   Serial.println("Invalid input! Please send one of the valid commands.");
  // }
    
  }

  // Check if the relay has been on for more than 10 seconds
  if (relayOn && (millis() - relayStartTime >= 10000)) {
    digitalWrite(relayPin, LOW); // Turn off the relay
    relayOn = false;             // Reset the relay state
    Serial.println("Relay turned off after 10s timeout.");
  }
// Đọc giá trị từ các cảm biến và in ra Serial Monitor
  for (int i = 0; i < 6; i++) {
    sensorValue[i] = digitalRead(sensorPin[i]);  // Đọc giá trị từ chân analog
    // Serial.print("Sensor ");
    // Serial.print(i);  // In ra chỉ số cảm biến
    // Serial.print(": ");
    // Serial.println(sensorValue[i]);  // In giá trị cảm biến
  }

  delay(1000);  // Đợi 1 giây trước khi đọc lại
}

// Servo movement functions (unchanged)
void getBook1(void) {
  moveServo(servo1, servo1Pin, 90, 135);
}
void getBook2(void) {
  moveServo(servo2, servo2Pin, 90, 135);
}
void getBook3(void) {
  moveServo(servo3, servo3Pin, 90, 133);
}
void getBook4(void) {
  moveServo(servo4, servo4Pin, 90, 125);
}
void getBook5(void) {
  moveServo(servo5, servo5Pin, 90, 135);
}
void getBook6(void) {
  moveServo(servo6, servo6Pin, 90, 135);
}

void moveServo(Servo &servo, int pin, int startAngle, int endAngle) {
  servo.attach(pin, minUs, maxUs);
  for (pos = startAngle; pos <= endAngle; pos++) {
    servo.write(pos);
    delay(50);
  }
  servo.write(startAngle);
  delay(1000);
  for (pos = startAngle; pos >= startAngle - (endAngle - startAngle); pos--) {
    servo.write(pos);
    delay(50);
  }
  servo.detach();
    // Turn on the relay and start the timer
    digitalWrite(relayPin, HIGH);
    relayStartTime = millis();
    relayOn = true;
}

void moveServo2(Servo &servo, int pin, int startAngle, int endAngle) {
  servo.attach(pin, minUs, maxUs);
  for (pos = startAngle; pos >= endAngle; pos--) {
    servo.write(pos);
    delay(50);
  }
  servo.write(startAngle);
  delay(1000);
  for (pos = startAngle; pos <= startAngle - (startAngle - endAngle); pos++) {
    servo.write(pos);
    delay(30);
  }
  servo.detach();
}
