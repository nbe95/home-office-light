#ifndef _ANIMATION_H_
#define _ANIMATION_H_

#include "timer.h"


// Base class for each animation
class Animation
{
public:
    typedef uint32_t color;
    static color rgb(uint8_t r, uint8_t g, uint8_t b)
    { return ((color)r << 8 | g) << 8 | b; };

    Animation() { start(); };
    void start() { m_timer.restart(); };
    virtual color getColor() = 0;

protected:
    Timer m_timer;
};


// Pulse wave animation
class WaveAnimation: public Animation
{
public:
    WaveAnimation(): Animation() {}
    void setBaseColor(const color base_color)
    { m_base_color = base_color; }
    void setPeriod(const Timer::ms period)
    { m_timer.setDuration(period); }
    void setMinMax(const uint8_t min, const uint8_t max)
    { m_min = min; m_max = max; }

    color getColor()
    {
        float cosine = 0;
        if (m_timer.getDuration() > 0)
            cosine = 0.5 * (cos(TWO_PI * m_timer.getElapsedTime() / m_timer.getDuration()) + 1);
        float brightness = cosine * (m_max - m_min) + m_min;

        color current_color = m_base_color;
        for (byte offset = 0; offset <= 16; offset += 8)
        {
            color component = ((current_color >> offset) & 0xFF) * brightness / 255;
            current_color &= ~((color)0xFF << offset);
            current_color |= (component << offset);
        }
        return current_color;
    };

private:
    color m_base_color;
    uint8_t m_min;
    uint8_t m_max;
};


// On-off animation
class OnOffAnimation: public Animation
{
public:
    OnOffAnimation(): Animation() {}
    void setBaseColor(const color base_color) { m_base_color = base_color; }
    void setOnOffTime(const Timer::ms on_time, const Timer::ms off_time)
    {
        m_on_time = on_time;
        m_off_time = off_time;
        m_timer.setDuration(m_on_time + m_off_time);
    }

    color getColor()
    {
        if (m_timer.check())
            m_timer.restart();

        if (m_timer.getElapsedTime() < m_on_time)
            return m_base_color;
        else
            return 0;
    };

private:
    color m_base_color;
    Timer::ms m_on_time;
    Timer::ms m_off_time;
};

#endif /* _ANIMATION_H_ */