
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
bool doorOpen = false;
bool buzzerPower = false;

// ------------------------
// ---- Device pins ------
// ------------------------

int fanPin = 6;
int buzzerPin = 3;
const unsigned int buzzerFrequency = 1000;

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
  delay(200);

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
  delay(200);

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
    dev3["capabilities"]["open"]["type"] = "boolean";
    dev3["capabilities"]["open"]["writable"] = true;
    dev3["state"]["open"] = doorOpen;
    serializeJson(d3, Serial);
    Serial.println();
  } // d3 freed here
  delay(200);

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
  delay(200);

  // ------------------------
  // -------- Buzzer --------
  // ------------------------
  // WRITABLE: server can turn it on/off

  {
    StaticJsonDocument<320> d5;
    d5["type"] = "CONNECT";
    JsonObject dev5 = d5["devices"]["buzzer-1"].to<JsonObject>();
    dev5["device_uuid"] = "buzzer-1";
    dev5["type"] = "buzzer";
    dev5["transport"]["mode"] = "via_controller";
    dev5["transport"]["controller_uuid"] = "arduino-1";
    dev5["transport"]["port"] = 3;
    dev5["capabilities"]["power"]["type"] = "boolean";
    dev5["capabilities"]["power"]["writable"] = true;
    dev5["state"]["power"] = buzzerPower;
    serializeJson(d5, Serial);
    Serial.println();
  }
  delay(200);
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

void setDoorOpen(bool open)
{
  doorOpen = open;

  if (doorOpen)
  {
    doorServo.write(180);
  }
  else
  {
    doorServo.write(0);
  }
}

void setBuzzerPower(bool enabled)
{
  buzzerPower = enabled;

  if (buzzerPower)
  {
    tone(buzzerPin, buzzerFrequency);
  }
  else
  {
    noTone(buzzerPin);
    digitalWrite(buzzerPin, LOW);
  }
}

void setup()
{
  pinMode(13, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  // For some reason HIGH is on, and LOW is off (Only fans)
  digitalWrite(fanPin, HIGH);
  setBuzzerPower(false);

  doorServo.attach(9);
  setDoorOpen(false);

  Serial.begin(9600);

  lcd.init();
  lcd.backlight();
  lcd.print("Smart House");
}

// ---------------------------
// ----- Recieve Command -----
// ---------------------------
void loop()
{
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
          setDoorOpen(state["open"]);
          lcd.clear();
          lcd.print(doorOpen ? "Door OPEN" : "Door CLOSED");
          StaticJsonDocument<64> s;
          s["open"] = doorOpen;
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
          setBuzzerPower(state["power"]);
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
