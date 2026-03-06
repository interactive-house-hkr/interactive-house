#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo doorServo;
Servo windowServo;

int fanSpeed = 0;
bool lightsOn = false;
bool doorOpen = false;
bool windowOpen = false;
bool lastDoorbellState = HIGH;
unsigned long doorbellMillis = 0;
bool doorbellActive = false;
unsigned long lastStatusMillis = 0;
const unsigned long STATUS_INTERVAL = 5000;
unsigned long lcdMsgMillis = 0;
const unsigned long LCD_MSG_DURATION = 3000;
bool lcdMsgActive = false;
bool isConnected = false;

void sendStatus()
{
  Serial.print("{\"type\":\"STATUS\",\"lights\":");
  Serial.print(lightsOn ? 1 : 0);
  Serial.print(",\"fan_speed\":");
  Serial.print(fanSpeed);
  Serial.print(",\"door\":\"");
  Serial.print(doorOpen ? "open" : "closed");
  Serial.print("\",\"window\":\"");
  Serial.print(windowOpen ? "open" : "closed");
  Serial.println("\"}");
}

void showDefault()
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Smart House");
  lcd.setCursor(0, 1);
  if (fanSpeed > 0)
  {
    lcd.print("Fan: " + String(fanSpeed) + "% speed");
  }
  else
  {
    lcd.print("All systems OK");
  }
}

void setup()
{
  pinMode(8, INPUT);
  pinMode(3, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(13, OUTPUT);
  pinMode(5, OUTPUT);

  doorServo.attach(9);
  doorServo.write(0);
  windowServo.attach(10);
  windowServo.write(0);

  Serial.begin(9600);
  lcd.init();
  lcd.backlight();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Smart House");
  lcd.setCursor(0, 1);
  lcd.print("Not connected");
}

void loop()
{
  // Listen for commands from Python bridge via Bluetooth
  if (Serial.available() > 0)
  {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "OK+CONN")
    {
      isConnected = true;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Connection");
      lcd.setCursor(0, 1);
      lcd.print("Successful!");
      lcdMsgActive = true;
      lcdMsgMillis = millis();
    }
    else if (cmd == "OK+LOST")
    {
      isConnected = false;
      lcdMsgActive = false;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Smart House");
      lcd.setCursor(0, 1);
      lcd.print("Not connected");
    }
    else if (cmd == "LIGHTS_ON")
    {
      lightsOn = true;
      digitalWrite(13, HIGH);
      digitalWrite(5, HIGH);
      if (!doorbellActive)
      {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Lights: ON");
        lcdMsgActive = true;
        lcdMsgMillis = millis();
      }
    }
    else if (cmd == "LIGHTS_OFF")
    {
      lightsOn = false;
      digitalWrite(13, LOW);
      digitalWrite(5, LOW);
      if (!doorbellActive)
      {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Lights: OFF");
        lcdMsgActive = true;
        lcdMsgMillis = millis();
      }
    }
    else if (cmd == "DOOR_OPEN")
    {
      doorOpen = true;
      doorServo.write(180);
      if (!doorbellActive)
      {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Door: OPEN");
        lcdMsgActive = true;
        lcdMsgMillis = millis();
      }
    }
    else if (cmd == "DOOR_CLOSE")
    {
      doorOpen = false;
      doorServo.write(0);
      if (!doorbellActive)
      {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Door: CLOSED");
        lcdMsgActive = true;
        lcdMsgMillis = millis();
      }
    }
    else if (cmd == "WINDOW_OPEN")
    {
      windowOpen = true;
      windowServo.write(110);
      if (!doorbellActive)
      {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Window: OPEN");
        lcdMsgActive = true;
        lcdMsgMillis = millis();
      }
    }
    else if (cmd == "WINDOW_CLOSE")
    {
      windowOpen = false;
      windowServo.write(0);
      if (!doorbellActive)
      {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Window: CLOSED");
        lcdMsgActive = true;
        lcdMsgMillis = millis();
      }
    }
    else if (cmd.startsWith("FAN_SPEED:"))
    {
      fanSpeed = constrain(cmd.substring(10).toInt(), 0, 100);
      digitalWrite(7, LOW);
      analogWrite(6, map(fanSpeed, 0, 100, 0, 255));
      if (!doorbellActive)
      {
        lcd.clear();
        lcd.setCursor(0, 0);
        if (fanSpeed > 0)
        {
          lcd.print("Fan: ON");
          lcd.setCursor(0, 1);
          lcd.print("Speed: " + String(fanSpeed) + "%");
        }
        else
        {
          lcd.print("Fan: OFF");
        }
        lcdMsgActive = true;
        lcdMsgMillis = millis();
      }
    }
  }

  // Return to default display after LCD message duration
  if (lcdMsgActive && !doorbellActive && millis() - lcdMsgMillis >= LCD_MSG_DURATION)
  {
    lcdMsgActive = false;
    showDefault();
  }

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
    showDefault();
  }

  // Periodic status report
  if (millis() - lastStatusMillis >= STATUS_INTERVAL)
  {
    lastStatusMillis = millis();
    sendStatus();
  }

  delay(50);
}
