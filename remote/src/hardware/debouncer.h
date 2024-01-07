// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_HARDWARE_DEBOUNCER_H_
#define SRC_HARDWARE_DEBOUNCER_H_

#include "Arduino.h"
#include "pin.h"
#include "../lib/timer/timer.h"


// Debouncer class for any kind of data type
template<class T>
class Debouncer {
 public:
    explicit Debouncer(Timer::ms threshold = 0) :               // Default constructor
    m_value(), m_debounced(), m_timer(threshold) {}

    // Getters for current state
    bool isReady() const            { return m_ready; }         // Check if a valid signal has been recorded yet
    const T& getDebounced() const   { return m_debounced; }     // Fetch debounced value
    const T& getRaw() const         { return m_value; }         // Fetch last recorded raw value
    bool hasChanged();                                          // Check if the signal has changed since the last call

    // Get/set the debouncing threshold
    void setThreshold(Timer::ms threshold)  { m_timer.setDuration(threshold); }
    Timer::ms getThreshold() const          { return m_timer.getDuration(); }

    // Setters, action events
    void debounce(T value);         // Update the internal value and performs the debouncing
    void reset();                   // Reset all internal states

    // Conversion operator
    explicit operator bool() const { return isReady(); }

 protected:
    T       m_value;                // Last recorded raw-value
    T       m_debounced;            // Processed debounced value
    bool    m_changed = false;      // State changed flag (persistent until queried)
    bool    m_ready = false;        // Flag indicating that a valid value has been processed
    Timer   m_timer;                // Internal timer
};


// Definition of template class functions

template<class T>
void Debouncer<T>::debounce(T value) {
    // Reset timer upon value change
    m_timer.start();
    if (value != m_value) {
        m_timer.restart();
        m_value = value;
    }

    // Fetch value changes
    if (!m_timer || m_timer.check()) {
        // Set ready flag once we have a stable value
        if (m_debounced != m_value) {
            m_debounced = m_value;
            m_changed |= m_ready;
        }
        m_ready = true;
    }
}

template<class T>
void Debouncer<T>::reset() {
    m_ready = false;
    m_changed = false;
    m_timer.reset();
}

template<class T>
bool Debouncer<T>::hasChanged() {
    // Note: This method is 'self-resetting'!
    // Call only once and store the return value as necessary.
    if (m_changed) {
        m_changed = false;
        return true;
    }
    return false;
}


// Class for buttons, switches and any type of binary sensors
class DebouncedSwitch : public Pin, public Debouncer<bool> {
 public:
    // Constructor
    explicit DebouncedSwitch(const Pin pin = Pin(), Timer::ms threshold = 0) :
    Pin(pin), Debouncer(threshold) {}

    // Switch state
    virtual void    debounce()              { if (isValid()) Debouncer::debounce(isLow()); }
    virtual bool    isOpen() const          { return !getDebounced(); }
    virtual bool    isClosed() const        { return getDebounced(); }
};

#endif  // SRC_HARDWARE_DEBOUNCER_H_
