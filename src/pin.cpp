// Copyright (c) 2022 Niklas Bettgen

#include "./pin.h" //NOLINT


// Serialization
int Pin::toString(char* const buffer) const {
    if (!isSet())
        return snprintf_P(buffer, 9, PSTR("X()"));

    uint8_t pin_number = getPin();
    if (isAnalog())
        pin_number -= A0;

    return snprintf_P(buffer, 9, PSTR("%s%s%s(%s%hhu)"),
        isOutput() ? "Q" : "I",
        hasPullUp() ? "P" : "",
        isInverted() ? "~" : "",
        isAnalog() ? "A" : "",
        pin_number);
}


// Definition of Pin class streaming operator overloads
Print& operator<<(Print& stream, const Pin& pin) {
    char buffer[9] = "";
    pin.toString(buffer);
    return stream << buffer;
}
