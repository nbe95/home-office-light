// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_MAP_H_
#define SRC_MAP_H_

#include "Arduino.h"


// Declaration of StaticMap template class
// To prevent heap fragmentation, a StaticMap acts as a fixed size container.
// Unlike a real std::map, data is never allocated dynamically.
template<class T, class U, int CAPACITY>
class StaticMap {
 public:
    struct pair { T key; U value; };                    // Definition of map data structure

    StaticMap();                                        // Default contructor
    StaticMap(const T& init_key, const U& init_value);  // Contructor providing explicit value initialization

    int         set(const T& key, const U& value);      // Adds a key-value pair or updates an existing one and returns the index

    int         getIndex(const T& key) const;           // Fetches the numerical index (=array position) of an element identified by its key
    U&          getValue(const T& key);                 // Fetches the value of an element identified by its key
    U&          getValueByIndex(const int index);       // Fetches the value of an element identified by its index
    T&          getKeyByIndex(const int index);         // Fetches the key of an element identified by its index
    bool        hasKey(const T& key);                   // Checks if a specific key is set
    bool        hasValue(const U& value);               // Checks if a specific value is set
    U&          operator[](const T& key);               // Operator for getting an element via square brackets

    void        clear();                                // Clears the entire content of the map
    void        dumps(Stream* const stream);            // Dumps the map's contents to a stream object

    using iter = pair*;                                 // Pointer type for data iteration
    iter        begin() { return &m_data[0]; }          // Returns a pointer to the start pair of the map
    iter        end() { return &m_data[m_size]; }       // Returns a pointer to the (current) end pait of the map
    iter        find(const T& key);                     // Returns a pointer to the (current) end pait of the map

    int         size() const            { return m_size; }                  // Returns the map's current size
    int         capacity() const        { return CAPACITY; }                // Returns the map's total capacity
    bool        empty() const           { return size() == 0; }             // Checks whether the map is currently empty
    bool        full() const            { return size() >= capacity(); }    // Checks whether the map is currently fully occupied
    size_t      storageSize() const     { return sizeof(pair) * size(); }   // Retreives the total size the map allocates in memory

 protected:
    pair        m_data[CAPACITY];                       // Internal array of fixed size
    int         m_size;                                 // Number of currently occupied items
};


// Definition of template class functions

template<class T, class U, int CAPACITY>
StaticMap<T, U, CAPACITY>::StaticMap() :
m_size(0) {}


template<class T, class U, int CAPACITY>
StaticMap<T, U, CAPACITY>::StaticMap(const T& init_key, const U& init_value) :
StaticMap() {
    for (int i = 0; i < CAPACITY; i++) {
        m_data[i].key   = init_key;
        m_data[i].value = init_value;
    }
}


template<class T, class U, int CAPACITY>
int StaticMap<T, U, CAPACITY>::set(const T& key, const U& value) {
    // Check if specified key already exists
    int index = getIndex(key);
    if (index < 0) {
        // Don't do anything if the map is already full
        if (size() >= capacity())
            return -1;

        // Use first empty item
        index = m_size++;
    }
    m_data[index].key   = key;
    m_data[index].value = value;
    return index;
}


template<class T, class U, int CAPACITY>
int StaticMap<T, U, CAPACITY>::getIndex(const T& key) const {
    for (int i = 0; i < size(); i++)
        if (m_data[i].key == key)
            return i;
    return -1;
}


template<class T, class U, int CAPACITY>
U& StaticMap<T, U, CAPACITY>::getValue(const T& key) {
    return getValueByIndex(getIndex(key));
}


template<class T, class U, int CAPACITY>
U& StaticMap<T, U, CAPACITY>::getValueByIndex(const int index) {
    return m_data[index].value;
}


template<class T, class U, int CAPACITY>
T& StaticMap<T, U, CAPACITY>::getKeyByIndex(const int index) {
    return m_data[index].key;
}


template<class T, class U, int CAPACITY>
void StaticMap<T, U, CAPACITY>::clear() {
    m_size = 0;
}


template<class T, class U, int CAPACITY>
bool StaticMap<T, U, CAPACITY>::hasKey(const T& key) {
    for (const pair* it = begin(); it < end(); it++)
        if (it->key == key)
            return true;
    return false;
}


template<class T, class U, int CAPACITY>
bool StaticMap<T, U, CAPACITY>::hasValue(const U& value) {
    for (const pair* it = begin(); it < end(); it++)
        if (it->value == value)
            return true;
    return false;
}


template<class T, class U, int CAPACITY>
void StaticMap<T, U, CAPACITY>::dumps(Stream* const stream) {
    char line[80] = {0};
    int i = 0;
    for (pair* it = begin(); it < end(); it++) {
        snprintf_P(line, sizeof(line), PSTR("[%03d]  "), i++);
        stream->print(line);
        stream->print(it->key);
        stream->print(F(" -> "));
        stream->println(it->value);
    }

    snprintf_P(line, sizeof(line), PSTR("Key/value/total size: %d/%d/%dB, %d/%d items allocated at: 0x%04X"),
        sizeof(T),
        sizeof(U),
        sizeof(*this),
        size(),
        capacity(),
        ADDR(m_data));
    stream->println(line);
}


template<class T, class U, int CAPACITY>
U& StaticMap<T, U, CAPACITY>::operator[](const T& key) {
    return getValue(key);
}


template<class T, class U, int CAPACITY>
typename StaticMap<T, U, CAPACITY>::pair* StaticMap<T, U, CAPACITY>::find(const T& key) {
    for (const pair* it = begin(); it < end(); it++)
        if (it->key == key)
            return it;
    return end();
}


#endif  // SRC_MAP_H_
