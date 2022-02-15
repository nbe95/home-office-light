// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_DEBOUNCER_H_
#define SRC_DEBOUNCER_H_

#include "Arduino.h"
#include "./pin.h"
#include "./timer.h"


// Debouncer class for any kind of data type
template<class T>
class Debouncer {
 public:
    // Constructor
    explicit Debouncer(Timer::ms threshold = 0) :
    m_value(),
    m_debounced(),
    m_timer(threshold) {}

    // Updates the internal value and performs the debouncing
    void debounce(T value) {
        // Reset timer upon value change
        m_timer.start();
        if (value != m_value) {
            m_timer.restart();
            m_value = value;
        }

        // Fetch value changes
        m_changed = false;
        if (m_timer.check()) {
            // Set ready flag once we have a stable value
            if (m_debounced != m_value) {
                m_debounced = m_value;
                m_changed |= m_ready;
            }
            m_ready = true;
        }
    }

    // Retreive the debounced or raw value
    bool isReady() const    { return m_ready; }
    T getDebounced() const  { return m_debounced; }
    T getRaw() const        { return m_value; }

    // Get/set the debouncing threshold
    void setThreshold(Timer::ms threshold)  { m_timer.setDuration(threshold); }
    Timer::ms getThreshold()                { return m_timer.getDuration(); }

    // Reset internal states
    void reset() {
        m_ready = false;
        m_changed = false;
        m_timer.reset();
    }

    // Fetch any signal edge
    bool hasChanged() {
        if (m_changed) {
            m_changed = false;
            return true;
        }
        return false;
    }

 protected:
    T       m_value;
    T       m_debounced;
    bool    m_changed = false;
    bool    m_ready = false;
    Timer   m_timer;
};


// Class for buttons, switches and any type of binary sensors
class DebouncedSwitch : public Debouncer<bool> {
 public:
    // Constructor
    explicit DebouncedSwitch(const Pin pin = Pin(), Timer::ms threshold = 0) :
    Debouncer(threshold),
    m_pin(pin) {}

    // Hardware setup
    void            setPin(const Pin pin)   { m_pin = pin; }
    Pin             getPin() const          { return m_pin; }

    // Debouncing
    virtual bool    readStatus() const      { return m_pin.isSet() && m_pin.isLow(); }
    virtual void    debounce()              { if (m_pin.isSet()) Debouncer::debounce(readStatus()); }

    // Switch status
    virtual bool    isOpen() const          { return !getDebounced(); }
    virtual bool    isClosed() const        { return getDebounced(); }

 protected:
    Pin             m_pin;
};

#endif  // SRC_DEBOUNCER_H_
