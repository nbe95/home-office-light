// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_HARDWARE_PIN_H_
#define SRC_HARDWARE_PIN_H_

#include <Streaming.h>
#include "../macros.h"

#define PIN_MODE_UNSET (uint8_t)0xFF


// Class for in-place handling of Arduino hardware pins
class Pin {
 public:
    static constexpr uint8_t invalid = 0;
    static constexpr uint8_t min_no = 1;
    static constexpr uint8_t max_no = PIN_A7;

    // Constructors
    explicit Pin(const uint8_t pin = 0, const uint8_t mode = PIN_MODE_UNSET, const bool invert = false) {
        setPin(pin);
        setMode(mode);
        setInvert(invert);
    }

    // Configuration setters
    void setPin(const uint8_t pin)      { BF_SET(m_pin_data, isPinValid(pin) ? pin : invalid, 0, 5); }
    void setMode(const uint8_t mode)    { BF_SET(m_pin_data, isModeValid(mode) ? mode : PIN_MODE_UNSET, 5, 2); }
    void setInvert(const bool invert)   { BF_SET(m_pin_data, (uint8_t)invert, 7, 1); }
    void setup() const                  { if (isValid()) pinMode(getPin(), getMode()); }

    // Configuration getters
    bool isValid() const                { return isPinValid(getPinInt()) && isModeValid(getModeInt()); }
    uint8_t getPin() const              { return isValid() ? getPinInt()                                      : invalid; }
    uint8_t getMode() const             { return isValid() ? getModeInt()                                     : PIN_MODE_UNSET; }
    bool isInverted() const             { return isValid() ? getInvertInt()                                   : false; }
    bool isInput() const                { return isValid() ? getMode() == INPUT || getMode() == INPUT_PULLUP  : false; }
    bool isOutput() const               { return isValid() ? getMode() == OUTPUT                              : false; }
    bool hasPullUp() const              { return isValid() ? getMode() == INPUT_PULLUP                        : false; }
    bool isAnalog() const               { return isValid() ? getPin() >= PIN_A0 && getPin() <= PIN_A7         : false; }

    // Value getters
    bool isHigh() const                 { return isValid() ? digitalRead(getPin()) == (isInverted() ? LOW : HIGH) : false; }
    bool isLow() const                  { return isValid() ? digitalRead(getPin()) == (isInverted() ? HIGH : LOW) : false; }
    int getAnalog() const               { return isValid() ? analogRead(getPin())                                 : 0; }
    float getAnalogScaled(const float in_min, const float in_max, const float out_min, const float out_max) const {
        return (getAnalog() - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
    }
    int toString(char* const buffer) const;

    // Value setters
    void setHigh() const                    { if (isValid()) digitalWrite(getPin(), isInverted() ? LOW : HIGH); }
    void setLow() const                     { if (isValid()) digitalWrite(getPin(), isInverted() ? HIGH : LOW); }
    void setAnalog(const int value) const   { if (isValid()) analogWrite(getPin(), value); }

    // Comparison operators
    bool operator==(const Pin& other) const { return getPin() == other.getPin(); }
    bool operator!=(const Pin& other) const { return getPin() != other.getPin(); }

    // Conversion operators
    explicit operator bool() const      { return isValid(); }
    operator uint8_t() const            { return m_pin_data; }

 protected:
    // Internal routines
    uint8_t getPinInt() const           { return BF_GET(m_pin_data, 0, 5); }
    uint8_t getModeInt() const          { return BF_GET(m_pin_data, 5, 2); }
    bool getInvertInt() const           { return (bool)BF_GET(m_pin_data, 7, 1); }

    bool isPinValid(const uint8_t pin) const    { return pin >= min_no && pin <= max_no; }
    bool isModeValid(const uint8_t mode) const  { return mode <= 0x02; }

    // Data storage
    uint8_t m_pin_data = 0;
};

// Declaration of stream operator overloads
Print& operator<<(Print& stream, const Pin& pin);


#endif  // SRC_HARDWARE_PIN_H_
