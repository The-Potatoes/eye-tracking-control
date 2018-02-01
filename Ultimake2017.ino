// declaration
const int lm1 = 10;
const int lm2 = 11;
const int rm1 = 5;
const int rm2 = 6;

const int backsig = 4;
const int brakesig = 2;
const int leftsig = 7;
const int rightsig = 8;

const int spd1 = 210;
const int spd2 = 250;

void setup() {
  Serial.begin(9600);
  pinMode (lm1, OUTPUT);
  pinMode (lm2, OUTPUT);
  pinMode (rm1, OUTPUT);
  pinMode (rm2, OUTPUT);
  pinMode (backsig, OUTPUT);
  pinMode (brakesig, OUTPUT);
  pinMode (leftsig, OUTPUT);
  pinMode (rightsig, OUTPUT);
}

void loop() {
  unsigned long cam_signal_avai = millis();
  // turn on headlight, always
  if(Serial.available() > 0){
    cam_signal_avai = millis();
    int inData = Serial.read()-'0';
    if (inData == 0) {
      digitalWrite (lm1, LOW); // brake
      digitalWrite (lm2, LOW);
      digitalWrite (rm1, LOW);
      digitalWrite (rm2, LOW);
      digitalWrite (leftsig, LOW);
      digitalWrite (rightsig, LOW);
      digitalWrite (brakesig, HIGH);
      digitalWrite (backsig, LOW);
      // turn on brakesig
    }
    if (inData == 1){
      analogWrite (lm1, spd2); // forward
      digitalWrite (lm2, LOW);
      analogWrite (rm1, spd2);
      digitalWrite (rm2, LOW);
      digitalWrite (leftsig, LOW);
      digitalWrite (rightsig, LOW);
      digitalWrite (brakesig, LOW);
      digitalWrite (backsig, LOW);
    }
    else if (inData == 2) {
      digitalWrite (lm1, LOW); // turn left
      analogWrite (lm2, 180);
      analogWrite (rm1, 180);
      digitalWrite (rm2, LOW);
      digitalWrite (leftsig, HIGH);
      digitalWrite (rightsig, LOW);
      digitalWrite (brakesig, LOW);
      digitalWrite (backsig, LOW);
      // turn on leftsig
    }
    else if (inData == 3) {
      analogWrite (lm1, 180); // turn right
      digitalWrite (lm2, LOW);
      digitalWrite (rm1, LOW);
      analogWrite (rm2, 180);
      digitalWrite (leftsig, LOW);
      digitalWrite (rightsig, HIGH);
      digitalWrite (brakesig, LOW);
      digitalWrite (backsig, LOW);
      // turn on rightsig
    }
    else if (inData == 4) {
      digitalWrite (lm1, LOW); // backward
      analogWrite (lm2, spd1);
      digitalWrite (rm1, LOW);
      analogWrite (rm2, spd1);
      digitalWrite (leftsig, LOW);
      digitalWrite (rightsig, LOW);
      digitalWrite (brakesig, LOW);
      digitalWrite (backsig, HIGH);
      // turn on backsig
    }
  }
  else{
    // lost signal more than 5 sec
    unsigned long cur = millis();
    if((unsigned long)(cur-cam_signal_avai) > 5000){
      // stop it
      digitalWrite (lm1, LOW); // brake
      digitalWrite (lm2, LOW)  ;
      digitalWrite (rm1, LOW);
      digitalWrite (rm2, LOW);
      digitalWrite (leftsig, LOW);
      digitalWrite (rightsig, LOW);
      digitalWrite (brakesig, HIGH);
      digitalWrite (backsig, LOW);
      // turn on brakesig
    }
  }
}
