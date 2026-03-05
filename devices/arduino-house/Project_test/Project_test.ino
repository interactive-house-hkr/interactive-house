#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo doorServo;

bool fanOn = false;
bool lastFanButtonState = HIGH;
bool lastDoorbellState = HIGH;
unsigned long doorbellMillis = 0;
bool doorbellActive = false;
unsigned long fanOffMillis = 0;
bool fanOffActive = false;

void showDefault()
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Smart House");
  lcd.setCursor(0, 1);
  lcd.print("All systems OK");
}

void setup()
{
  pinMode(4, INPUT);
  pinMode(8, INPUT);
  pinMode(3, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(13, OUTPUT);
  pinMode(5, OUTPUT);

  doorServo.attach(9);
  doorServo.write(0);

  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  showDefault();
}

void loop()
{
  // Listen for commands from Python bridge via Bluetooth
  if (Serial.available() > 0)
  {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    Serial.println("Received: " + cmd);
    cmd.trim();

    if (cmd == "LIGHTS_ON")
    {
      digitalWrite(13, HIGH);
      digitalWrite(5, HIGH);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Lights: ON");
    }
    else if (cmd == "LIGHTS_OFF")
    {
      digitalWrite(13, LOW);
      digitalWrite(5, LOW);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Lights: OFF");
    }
    else if (cmd == "DOOR_OPEN")
    {
      doorServo.write(180);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Door: OPEN");
    }
    else if (cmd == "DOOR_CLOSE")
    {
      doorServo.write(0);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Door: CLOSED");
    }
  }

  // Fan button (D4)
  bool fanButtonState = digitalRead(4);
  if (lastFanButtonState == HIGH && fanButtonState == LOW)
  {
    fanOn = !fanOn;
    digitalWrite(7, LOW);
    digitalWrite(6, fanOn ? HIGH : LOW);
    Serial.println(fanOn ? "{\"event\":\"FAN_ON\"}" : "{\"event\":\"FAN_OFF\"}");

    if (!doorbellActive)
    {
      lcd.clear();
      lcd.setCursor(0, 0);
      if (fanOn)
      {
        fanOffActive = false;
        lcd.print("Fan: ON");
        lcd.setCursor(0, 1);
        lcd.print("Full Speed");
      }
      else
      {
        fanOffActive = true;
        fanOffMillis = millis();
        lcd.print("Fan: OFF");
      }
    }
  }
  lastFanButtonState = fanButtonState;

  // Doorbell (D8)
  bool doorbellState = digitalRead(8);
  if (lastDoorbellState == HIGH && doorbellState == LOW)
  {
    tone(3, 589);
    delay(300);
    noTone(3);
    doorbellActive = true;
    doorbellMillis = millis();
    Serial.println("{\"event\":\"DOORBELL\"}");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("** DOORBELL **");
    lcd.setCursor(0, 1);
    lcd.print("Someone's there!");
  }
  lastDoorbellState = doorbellState;

  if (doorbellActive && millis() - doorbellMillis >= 5000)
  {
    doorbellActive = false;
    if (fanOn)
    {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Fan: ON");
      lcd.setCursor(0, 1);
      lcd.print("Full Speed");
    }
    else
    {
      showDefault();
    }
  }

  if (fanOffActive && millis() - fanOffMillis >= 3000)
  {
    fanOffActive = false;
    if (!doorbellActive)
      showDefault();
  }

  delay(50);
}