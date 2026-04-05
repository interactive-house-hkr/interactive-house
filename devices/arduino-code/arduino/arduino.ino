
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
  } // d1 freed here
  delay(150);

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
