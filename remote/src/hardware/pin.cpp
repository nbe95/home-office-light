// Copyright (c) 2022 Niklas Bettgen

#include "pin.h"


// Serialization
int Pin::toString(char* const buffer) const {
    if (!isValid())
        return snprintf_P(buffer, 9, PSTR("X[]"));

    return snprintf_P(buffer, 9, PSTR("%s%s%s[%s%hhu]"),
        isOutput() ? "Q" : "I",
        hasPullUp() ? "P" : "",
        isInverted() ? "~" : "",
        isAnalog() ? "A" : "",
        getPin() - (isAnalog() ? PIN_A0 : 0));
}


// Definition of Pin class streaming operator overloads
Print& operator<<(Print& stream, const Pin& pin) {
    char buffer[9] = "";
    pin.toString(buffer);
    return stream << buffer;
}
