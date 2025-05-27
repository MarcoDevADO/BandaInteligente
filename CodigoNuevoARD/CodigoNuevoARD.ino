#include <Servo.h>

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

bool moviendoServo = false;
unsigned long tiempoInicioServo = 0;
const unsigned long duracionServo = 2000;

Servo myServo;
int servoPin = 11;
int servoPos = 0;

int boton = 2;  // Botón para parar motor (como 'P')
int valorboton;
int valanterior = HIGH;

int ledV = 8;
int ledN = 9;
int derecha = 6;
int izquierda = 7;
int enable = 4;

bool motorActivo = false;
int memoria = 1;  // Banda encendida por defecto

void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);

  pinMode(boton, INPUT_PULLUP);
  pinMode(enable, INPUT_PULLUP);

  pinMode(ledV, OUTPUT);
  pinMode(ledN, OUTPUT);
  pinMode(izquierda, OUTPUT);
  pinMode(derecha, OUTPUT);
  myServo.write(0);
}

void loop() {
  // Detener motor si se presiona el botón (como 'P')
  valorboton = digitalRead(boton);
  if ((valorboton == LOW) && (valanterior == HIGH)) {
    if ((millis() - lastDebounceTime) > debounceDelay) {
      analogWrite(derecha, 0);
      analogWrite(izquierda, 0);
      motorActivo = false;
      lastDebounceTime = millis();
    }
  }
  valanterior = valorboton;

  // Control del servo
  if (moviendoServo && (millis() - tiempoInicioServo >= duracionServo)) {
    myServo.write(0);
    moviendoServo = false;
  }

  // Control de la banda (si memoria = 1 y enable = LOW)
  if (memoria == 1 && digitalRead(enable) == LOW) {
    if (!motorActivo) {
      analogWrite(derecha, 180);
      motorActivo = true;
    }
  } else {
    if (motorActivo) {
      analogWrite(derecha, 0);
      motorActivo = false;
    }
  }

  // Comandos Serial
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    input.toUpperCase();

    if (input == "D") {
      analogWrite(izquierda, 255);
      analogWrite(derecha, 0);
    } else if (input == "I") {
      analogWrite(izquierda, 0);
      analogWrite(derecha, 255);
    } else if (input == "SERVO_ON") {
      myServo.write(90);
      moviendoServo = true;
      tiempoInicioServo = millis();
    } else if (input == "LEN_T") {
      digitalWrite(ledV, HIGH);
      digitalWrite(ledN, LOW);
    } else if (input == "LED_F") {
      digitalWrite(ledV, LOW);
      digitalWrite(ledN, HIGH);
    } else if (input == "LED_OFF") {
      digitalWrite(ledV, LOW);
      digitalWrite(ledN, LOW);
    } else if (input == "ENCENDER_BANDA") {
      memoria = 1;
    } else if (input == "DETENER_BANDA") {
      memoria = 0;
    } else if (input == "P") {
      analogWrite(derecha, 0);
      analogWrite(izquierda, 0);
      motorActivo = false;
    } else {
      Serial.println(input);
    }
  }
}