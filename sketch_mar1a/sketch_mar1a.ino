#include <ESP8266WiFi.h>  // <-- This is the only line that changed!
#include <WiFiUdp.h>

// --- NETWORK CONFIGURATION ---
const char* ssid = "Mohit";     // Enter your Wi-Fi name
const char* password = "88888888";     // Enter your Wi-Fi password
const char* target_ip = "192.168.137.102";           // ENTER YOUR LAPTOP'S IP HERE!
const int udp_port = 5005;                       // Tactical Telemetry Port

WiFiUDP udp;

// --- DRONE STATE (Faking the GPS) ---
int drone_id = 2; // We are assigning the ESP-12F to be Drone #2
float pos_x = 400.0;
float pos_y = 300.0;
int battery = 95;

void setup() {
  Serial.begin(115200);
  
  // 1. Connect to the Network
  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[LINK ESTABLISHED] IP: " + WiFi.localIP().toString());
}

void loop() {
  // 2. Simulate Drone Flight (Orbiting slightly)
  pos_x += random(-3, 4); 
  pos_y += random(-3, 4);
  
  // Keep it on the radar screen
  if(pos_x < 50) pos_x = 50; if(pos_x > 750) pos_x = 750;
  if(pos_y < 50) pos_y = 50; if(pos_y > 550) pos_y = 550;

  // 3. Format the Telemetry Packet ("ID,X,Y,BATTERY")
  String packet = String(drone_id) + "," + String(pos_x) + "," + String(pos_y) + "," + String(battery);
  
  // 4. Fire the Packet to the Laptop via UDP
  udp.beginPacket(target_ip, udp_port);
  udp.print(packet);
  udp.endPacket();

  Serial.println("Sent telemetry: " + packet);
  
  // Transmit at 10Hz (100ms delay)
  delay(100); 
}