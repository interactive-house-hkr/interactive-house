
// ---------------------
// ----- Libraries -----
// ---------------------
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <ArduinoJson.h>
// Added library SoftwareSerial
// #include <SoftwareSerial.h>

// SoftwareSerial btSerial(0, 1);

LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo doorServo;

unsigned long lastHeartbeat = 0;

// ------------------------
// ----- Device State -----
// ------------------------
bool lightPower = false;
bool fanPower = false;
int fanPin = 6;
String doorState = "closed";

// ------------------------
// ----- Send Connect -----
// ------------------------
void sendConnect()
{
  // Send devices one at a time to avoid RAM overflow

  // Controller
  StaticJsonDocument<128> d1;
  d1["type"] = "CONNECT";
  d1["device_uuid"] = "arduino-1";
  d1["device_type"] = "controller";
  serializeJson(d1, Serial);
  Serial.println();
  delay(100);

  // Light
  StaticJsonDocument<128> d2;
  d2["type"] = "CONNECT";
  d2["device_uuid"] = "light-1";
  d2["device_type"] = "light";
  d2["power"] = lightPower;
  serializeJson(d2, Serial);
  Serial.println();
  delay(100);

  // Door
  StaticJsonDocument<128> d3;
  d3["type"] = "CONNECT";
  d3["device_uuid"] = "door-1";
  d3["device_type"] = "door";
  d3["open"] = doorState;
  serializeJson(d3, Serial);
  Serial.println();
  delay(100);

  // Fan
  StaticJsonDocument<128> d4;
  d4["type"] = "CONNECT";
  d4["device_uuid"] = "fan-1";
  d4["device_type"] = "fan";
  d4["power"] = fanPower;
  serializeJson(d4, Serial);
  Serial.println();
}

// --------------------------
// ----- Send Heartbeat -----
// --------------------------
void sendHeartbeat()
{
  StaticJsonDocument<128> doc;
  doc["type"] = "HEARTBEAT";
  doc["device_uuid"] = "arduino-1";

  serializeJson(doc, Serial);
  Serial.println();
}

// --------------------------------
// ----- Send Acknowledgement -----
// --------------------------------

void sendAck(const char *device, JsonObject state)
{
  StaticJsonDocument<256> doc;

  doc["type"] = "COMMAND_ACK";
  doc["device_uuid"] = device;
  doc["status"] = "ok";

  doc["reported_state"] = state;
  serializeJson(doc, Serial);
  Serial.println();
}

void setup()
{
  pinMode(13, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(fanPin, OUTPUT);

  // For some reason HIGH is on, and LOW is off
  digitalWrite(fanPin, HIGH);

  doorServo.attach(9);
  doorServo.write(0);

  Serial.begin(9600);

  lcd.begin();
  lcd.backlight();
  lcd.print("Smart House");

  // delay(1000);
  // sendConnect();
}

// ---------------------------
// ----- Recieve Command -----
// ---------------------------
void loop()
{
  if (Serial.available())
  {
    String input = Serial.readStringUntil('\n');
    input.trim();
    // Confirm data is being sent
    lcd.clear();
    lcd.print(input.substring(0, 16));

    StaticJsonDocument<256> doc;
    DeserializationError err = deserializeJson(doc, input);

    if (err)
    {
      Serial.println("{\"error\":\"invalid_json\"}");
      return;
    }

    const char *type = doc["type"];
    const char *device = doc["device_uuid"];

    // Only process commands
    if (strcmp(type, "COMMAND") == 0)
    {

      JsonObject state = doc["state"];
      // -----------------
      // ----- Light -----
      // -----------------
      if (strcmp(device, "light-1") == 0)
      {
        if (state.containsKey("power"))
        {
          lightPower = state["power"];

          digitalWrite(13, lightPower ? HIGH : LOW);
          digitalWrite(5, lightPower ? HIGH : LOW);

          lcd.clear();
          lcd.print(lightPower ? "Lights ON" : "Lights OFF");

          StaticJsonDocument<64> s;
          s["power"] = lightPower;
          sendAck("light-1", s.as<JsonObject>());
        }
      }
      // ----------------
      // ----- DOOR -----
      // ----------------
      if (strcmp(device, "door-1") == 0)
      {
        if (state.containsKey("open"))
        {
          doorState = state["open"].as<String>();

          if (doorState == "open")
          {
            doorServo.write(180);
            lcd.clear();
            lcd.print("Door OPEN");
          }
          else
          {
            doorServo.write(0);
            lcd.clear();
            lcd.print("Door CLOSED");
          }

          StaticJsonDocument<64> s;
          s["open"] = doorState;
          sendAck("door-1", s.as<JsonObject>());
        }
      }

      // Fan
      if (strcmp(device, "fan-1") == 0)
      {
        if (state.containsKey("power"))
        {
          fanPower = state["power"];

          digitalWrite(fanPin, fanPower ? LOW : HIGH);

          lcd.clear();
          lcd.print(fanPower ? "FAN ON" : "FAN OFF");

          StaticJsonDocument<64> s;
          s["power"] = fanPower;
          sendAck("fan-1", s.as<JsonObject>());
        }
      }
    }
    // ----------------------------------------------
    // Ping the server for connection and send info AFTER it connects
    // ----------------------------------------------
    if (strcmp(type, "PING") == 0)
    {
      sendConnect();
    }
  }
  // -----------------------------
  // ----- Heartbeat each 5s -----
  // -----------------------------
  if (millis() - lastHeartbeat > 5000)
  {
    sendHeartbeat();
    lastHeartbeat = millis();
  }

  delay(50);
}
