
// ---------------------
// ----- Libraries -----
// ---------------------
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <ArduinoJson.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo doorServo;

unsigned long lastHeartbeat = 0;

// ------------------------
// ----- Device States -----
// ------------------------
bool lightPower = false;
bool fanPower = false;
String doorState = "closed";
bool motionState = false;
bool buzzerPower = false;
int lightLevel = 0;

// ------------------------
// ---- Device pins ------
// ------------------------

int fanPin = 6;
int pirPin = A0;
int buzzerPin = 3;
int lightSensorPin = A2;

// Previous sensor readings to detect change
bool prevMotion = false;
int prevLightLevel = 0;

// ------------------------
// ----- Send Connect -----
// ------------------------
void sendConnect()
{

  // ------------------------
  // ----- Controller -------
  // ------------------------
  {
    StaticJsonDocument<320> d1;
    d1["type"] = "CONNECT";
    JsonObject dev1 = d1["devices"]["arduino-1"].to<JsonObject>();
    dev1["device_uuid"] = "arduino-1";
    dev1["type"] = "controller";
    dev1["transport"]["mode"] = "direct";
    dev1["transport"]["protocol"] = "ble";
    dev1["transport"]["service"] = "HMSoft";
    dev1["status"]["connected"] = true;
    serializeJson(d1, Serial);
    Serial.println();
  } // d1 is freed here
  delay(150);

  // ------------------------
  // -------- Light ---------
  // ------------------------
  {
    StaticJsonDocument<320> d2;
    d2["type"] = "CONNECT";
    JsonObject dev2 = d2["devices"]["light-1"].to<JsonObject>();
    dev2["device_uuid"] = "light-1";
    dev2["type"] = "light";
    dev2["transport"]["mode"] = "via_controller";
    dev2["transport"]["controller_uuid"] = "arduino-1";
    dev2["transport"]["port"] = 13;
    dev2["capabilities"]["power"]["type"] = "boolean";
    dev2["capabilities"]["power"]["writable"] = true;
    dev2["state"]["power"] = lightPower;
    serializeJson(d2, Serial);
    Serial.println();
  } // d2 freed here
  delay(150);

  // ------------------------
  // --------- Door ---------
  // ------------------------
  {
    StaticJsonDocument<320> d3;
    d3["type"] = "CONNECT";
    JsonObject dev3 = d3["devices"]["door-1"].to<JsonObject>();
    dev3["device_uuid"] = "door-1";
    dev3["type"] = "door";
    dev3["transport"]["mode"] = "via_controller";
    dev3["transport"]["controller_uuid"] = "arduino-1";
    dev3["transport"]["port"] = 9;
    dev3["capabilities"]["open"]["type"] = "string";
    dev3["capabilities"]["open"]["writable"] = true;
    dev3["state"]["open"] = doorState;
    serializeJson(d3, Serial);
    Serial.println();
  } // d3 freed here
  delay(150);

  // ------------------------
  // ---------- Fan ---------
  // ------------------------
  {
    StaticJsonDocument<320> d4;
    d4["type"] = "CONNECT";
    JsonObject dev4 = d4["devices"]["fan-1"].to<JsonObject>();
    dev4["device_uuid"] = "fan-1";
    dev4["type"] = "fan";
    dev4["transport"]["mode"] = "via_controller";
    dev4["transport"]["controller_uuid"] = "arduino-1";
    dev4["transport"]["port"] = 6;
    dev4["capabilities"]["power"]["type"] = "boolean";
    dev4["capabilities"]["power"]["writable"] = true;
    dev4["state"]["power"] = fanPower;
    serializeJson(d4, Serial);
    Serial.println();
  } // d4 freed here
  delay(150);

  // ------------------------
  // ---- Motion Sensor -----
  // ------------------------
  // READ-ONLY: writable=false, server cannot control it

  {
    StaticJsonDocument<320> d5;
    d5["type"] = "CONNECT";
    JsonObject dev5 = d5["devices"]["pir-1"].to<JsonObject>();
    dev5["device_uuid"] = "pir-1";
    dev5["type"] = "motion_sensor";
    dev5["transport"]["mode"] = "via_controller";
    dev5["transport"]["controller_uuid"] = "arduino-1";
    dev5["transport"]["port"] = A0;
    dev5["capabilities"]["motion"]["type"] = "boolean";
    dev5["capabilities"]["motion"]["writable"] = false;
    dev5["state"]["motion"] = motionState;
    serializeJson(d5, Serial);
    Serial.println();
  }
  delay(150);

  // ------------------------
  // -------- Buzzer --------
  // ------------------------
  // WRITABLE: server can turn it on/off

  {
    StaticJsonDocument<320> d6;
    d6["type"] = "CONNECT";
    JsonObject dev6 = d6["devices"]["buzzer-1"].to<JsonObject>();
    dev6["device_uuid"] = "buzzer-1";
    dev6["type"] = "buzzer";
    dev6["transport"]["mode"] = "via_controller";
    dev6["transport"]["controller_uuid"] = "arduino-1";
    dev6["transport"]["port"] = 3;
    dev6["capabilities"]["power"]["type"] = "boolean";
    dev6["capabilities"]["power"]["writable"] = true;
    dev6["state"]["power"] = buzzerPower;
    serializeJson(d6, Serial);
    Serial.println();
  }
  delay(150);

  // ------------------------
  // ------ Light Sensor ----
  // ------------------------
  // READ-ONLY: reports ambient light level 0-1023

  {
    StaticJsonDocument<320> d7;
    d7["type"] = "CONNECT";
    JsonObject dev7 = d7["devices"]["light-sensor-1"].to<JsonObject>();
    dev7["device_uuid"] = "light-sensor-1";
    dev7["type"] = "light_sensor";
    dev7["transport"]["mode"] = "via_controller";
    dev7["transport"]["controller_uuid"] = "arduino-1";
    dev7["transport"]["port"] = A2;
    dev7["capabilities"]["level"]["type"] = "integer";
    dev7["capabilities"]["level"]["min"] = 0;
    dev7["capabilities"]["level"]["max"] = 1023;
    dev7["capabilities"]["level"]["writable"] = false;
    dev7["state"]["level"] = lightLevel;
    serializeJson(d7, Serial);
    Serial.println();
  }
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

// ----------------------------------
// ----- Send Sensor State Update -----
// ----------------------------------
void sendStateUpdate(const char *device_uuid, JsonObject state)
{
  StaticJsonDocument<128> doc;
  doc["type"] = "STATE_UPDATE";
  doc["device_uuid"] = device_uuid;
  doc["state"] = state;
  serializeJson(doc, Serial);
  Serial.println();
}

void setup()
{
  pinMode(13, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(pirPin, INPUT);
  pinMode(buzzerPin, OUTPUT);

  // For some reason HIGH is on, and LOW is off (Only fans)
  digitalWrite(fanPin, HIGH);
  // Set buzzer as off by default
  digitalWrite(buzzerPin, LOW);

  doorServo.attach(9);
  doorServo.write(0);

  Serial.begin(9600);

  lcd.begin();
  lcd.backlight();
  lcd.print("Smart House");

  // Take initial sensor readings
  motionState = digitalRead(pirPin);
  lightLevel = analogRead(lightSensorPin);
  prevMotion = motionState;
  prevLightLevel = lightLevel;
}

// ---------------------------
// ----- Recieve Command -----
// ---------------------------
void loop()
{
  // ----------------------------------------
  // Read sensors and send updates on change
  // ----------------------------------------

  // Motion sensor
  bool newMotion = digitalRead(pirPin);
  if (newMotion != prevMotion)
  {
    motionState = newMotion;
    prevMotion = newMotion;

    lcd.clear();
    lcd.print(motionState ? "Motion ON" : "Motion OFF");

    StaticJsonDocument<64> s;
    s["motion"] = motionState;
    sendStateUpdate("pir-1", s.as<JsonObject>());
  }

  // Light sensor — only send update if change is significant (>10 units)
  int newLight = analogRead(lightSensorPin);
  if (abs(newLight - prevLightLevel) > 10)
  {
    lightLevel = newLight;
    prevLightLevel = newLight;

    StaticJsonDocument<64> s;
    s["level"] = lightLevel;
    sendStateUpdate("light-sensor-1", s.as<JsonObject>());
  }

  // ----------------------------------------
  // Handle incoming BLE commands
  // ----------------------------------------
  if (Serial.available())
  {
    String input = Serial.readStringUntil('\n');
    input.trim();

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
      // Light
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

      // -----------------
      // Door
      // -----------------
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

      // -----------------
      // Fan
      // -----------------
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

      // -----------------
      // Buzzer
      // -----------------
      if (strcmp(device, "buzzer-1") == 0)
      {
        if (state.containsKey("power"))
        {
          buzzerPower = state["power"];
          digitalWrite(buzzerPin, buzzerPower ? HIGH : LOW);
          lcd.clear();
          lcd.print(buzzerPower ? "BUZZER ON" : "BUZZER OFF");
          StaticJsonDocument<64> s;
          s["power"] = buzzerPower;
          sendAck("buzzer-1", s.as<JsonObject>());
        }
      }
    }

    // PING — resend all device registrations
    if (strcmp(type, "PING") == 0)
    {
      sendConnect();
    }
  }

  // -----------------------------
  // Heartbeat each 5s
  // -----------------------------
  if (millis() - lastHeartbeat > 5000)
  {
    sendHeartbeat();
    lastHeartbeat = millis();
  }

  delay(50);
}