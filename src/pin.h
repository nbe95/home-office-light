// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_PIN_H_
#define SRC_PIN_H_

#include <Streaming.h>
#include "Arduino.h"


// Class for in-place handling of Arduino hardware pins
class Pin {
 public:
    // Constructors
    explicit Pin(const uint8_t pin = 0) : m_pin_data(pin) {}
    explicit Pin(const uint8_t pin, const uint8_t mode, const bool invert = false) {
        setPin(pin);
        setMode(mode);
        setInvert(invert);
    }

    // Configuration setters
    void setPin(const uint8_t pin)      { m_pin_data &= (uint8_t)0b11100000; m_pin_data |= (pin     & (uint8_t)0b00011111); }
    void setMode(const uint8_t mode)    { m_pin_data &= (uint8_t)0b10011111; m_pin_data |= (mode    & (uint8_t)0b00000011) << 5; }
    void setInvert(const bool invert)   { m_pin_data &= (uint8_t)0b01111111; m_pin_data |= (invert  ? (uint8_t)0b10000000 : (uint8_t)0); }
    void setup() const                  { pinMode(getPin(), getMode()); }

    // Configuration getters
    uint8_t getPin() const              { return m_pin_data         & (uint8_t)0b00011111; }
    uint8_t getMode() const             { return (m_pin_data >> 5)  & (uint8_t)0b00000011; }
    bool isInverted() const             { return (m_pin_data        & (uint8_t)0b10000000) != 0; }
    bool isSet() const                  { return getPin() != 0; }
    bool isInput() const                { return getMode() == INPUT || getMode() == INPUT_PULLUP; }
    bool isOutput() const               { return getMode() == OUTPUT; }
    bool hasPullUp() const              { return getMode() == INPUT_PULLUP; }
    bool isAnalog() const               { return getPin() >= A0 && getPin() <= A7; }

    // Value getters
    bool isHigh() const                 { return digitalRead(getPin()) == (isInverted() ? LOW : HIGH); }
    bool isLow() const                  { return digitalRead(getPin()) == (isInverted() ? HIGH : LOW); }
    int getAnalog() const               { return analogRead(getPin()); }
    float getAnalogScaled(const float in_min, const float in_max, const float out_min, const float out_max) const {
        return (getAnalog() - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
    }
    int toString(char* const buffer) const;

    // Value setters
    void setHigh() const                    { digitalWrite(getPin(), isInverted() ? LOW : HIGH); }
    void setLow() const                     { digitalWrite(getPin(), isInverted() ? HIGH : LOW); }
    void setAnalog(const int value) const   { analogWrite(getPin(), value); }

    // Comparison operators
    bool operator==(const Pin& other) const { return getPin() == other.getPin(); }
    bool operator!=(const Pin& other) const { return getPin() != other.getPin(); }

    // Conversion operators
    explicit operator bool() const  { return isSet(); }
    operator uint8_t() const        { return (uint8_t)m_pin_data; }

 protected:
    uint8_t m_pin_data;
};

// Declaration of stream operator overloads
Print& operator<<(Print& stream, const Pin& pin);


#endif  // SRC_PIN_H_
