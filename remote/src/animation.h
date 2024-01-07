// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_ANIMATION_H_
#define SRC_ANIMATION_H_

#include "lib/timer/timer.h"


// Base class for each animation
class Animation {
 public:
    typedef uint32_t color;
    static uint8_t Red(const color color) { return (color >> 16) & 0xFF; }
    static uint8_t Green(const color color) { return (color >> 8) & 0xFF; }
    static uint8_t Blue(const color color) { return (color >> 0) & 0xFF; }
    static color RGB(const uint8_t r, const uint8_t g, const uint8_t b) { return ((color)r << 8 | g) << 8 | b; }

    explicit Animation(const Timer::ms period) : m_timer(Timer(period)) { start(); }
    virtual void start() { m_timer.restart(); }
    virtual color getColor() = 0;

 protected:
    Timer m_timer;
};


// Pulse wave animation
class WaveAnimation: public Animation {
 public:
    explicit WaveAnimation(const Timer::ms period) : Animation(period) {}
    void setBaseColor(const color base_color) { m_base_color = base_color; }
    void setMinMax(const uint8_t min, const uint8_t max) { m_min = min; m_max = max; }

    color getColor() {
        float cosine = 0;
        if (m_timer.getDuration() > 0)
            cosine = 0.5 * (cos(TWO_PI * m_timer.getElapsedTime() / m_timer.getDuration()) + 1);
        float scaling = (cosine * (m_max - m_min) + m_min) / 255;

        return RGB(
            Red(m_base_color) * scaling,
            Green(m_base_color) * scaling,
            Blue(m_base_color) * scaling);
    }

 private:
    color               m_base_color;
    uint8_t             m_min = 0;
    uint8_t             m_max = 255;
};


// On-off animation
class OnOffAnimation: public Animation {
 public:
    OnOffAnimation(const Timer::ms time_on, const Timer::ms time_off) :
    m_time_on(time_on),
    m_time_off(time_off),
    Animation(time_on + time_off) {}
    void setBaseColor(const color base_color) { m_base_color = base_color; }

    color getColor() {
        m_timer.checkAndRestart();
        if (m_timer.getElapsedTime() < m_time_on)
            return m_base_color;
        else
            return 0;
    }

 private:
    const Timer::ms m_time_on;
    const Timer::ms m_time_off;
    color m_base_color;
};


// Rainbow animation
class RainbowAnimation: public Animation {
 public:
    explicit RainbowAnimation(const Timer::ms period) : Animation(period / 6) {}
    void start() { Animation::start(); m_phase = 0; }

    color getColor() {
        if (m_timer.checkAndRestart()) {
            if (++m_phase >= 6)
                m_phase = 0;
        }

        uint8_t fade_value = m_timer.getElapsedTimeRel() * 255;
        switch (m_phase) {
            case 0:
                return RGB(255, fade_value, 0);
            case 1:
                return RGB(255 - fade_value, 255, 0);
            case 2:
                return RGB(0, 255, fade_value);
            case 3:
                return RGB(0, 255 - fade_value, 255);
            case 4:
                return RGB(fade_value, 0, 255);
            case 5:
                return RGB(255, 0, 255 - fade_value);
        }
        return 0;
    }

 private:
    int m_phase = 0;
};

#endif  // SRC_ANIMATION_H_
