// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_CONTAINER_MAP_H_
#define SRC_CONTAINER_MAP_H_


// Declaration of StaticMap template class
// To prevent heap fragmentation, a StaticMap acts as a fixed size container.
// Unlike a real std::map, data is never allocated dynamically.
template<class T, class U>
class StaticMap {
 public:
    struct pair { T key; U value; };                        // Definition of map data structure

    explicit StaticMap(
        const int capacity,
        const T& fallback_key = T(),
        const U& fallback_value = U());                     // Contructor providing explicit value initialization

    int             set(const T& key, const U& value);      // Add a key-value pair or update an existing one and return the index

    const U&        get(const T& key) const;                // Fetch a read-only reference to an element's value
    const U&        getByIndex(const int index) const;      // Fetch the value of an element identified by its index
    const T&        getKeyByIndex(const int index) const;   // Fetch the key of an element identified by its index
    bool            has(const U& value) const;              // Check if a specific value is set
    bool            hasKey(const T& key) const;             // Check if a specific key is set
    int             getIndex(const T& key) const;           // Fetch the numerical index (=array position) of an element identified by its key

    void            clear();                                                        // Clear the entire content of the map
    void            dump(Stream* const stream, const int indent = 0) const;         // Dump the map's contents to a stream object

    using iter = const pair*;                                   // Pointer type for data iteration
    iter            begin() const { return &m_data[0]; }        // Return a pointer to the start pair of the map
    iter            end() const { return &m_data[m_size]; }     // Return a pointer to the (current) end pait of the map
    iter            find(const T& key) const;                   // Return a pointer to the (current) end pait of the map

    int             size() const            { return m_size; }                      // Return the map's current size
    int             capacity() const        { return m_capacity; }                  // Return the map's total capacity
    bool            empty() const           { return size() == 0; }                 // Check whether the map is currently empty
    bool            full() const            { return size() >= capacity(); }        // Check whether the map is currently fully occupied
    size_t          storageSize() const     { return sizeof(pair) * capacity(); }   // Retrieve the total size the map allocates in memory

    const U&        operator[](const T& key) const { return get(key); }             // Square bracket operator for read-only data access

 protected:
    bool            indexIsValid(const int index) const { return index >= 0 && index < size(); }    // Returns true if the provided index is valid
    const int       m_capacity;                             // Total number of items allocated in memory
    const pair      m_fallback;                             // Fallback values for out-of-bounds access etc.
    int             m_size;                                 // Number of currently occupied items
    pair*           m_data;                                 // Internal array of fixed size
};


// Definition of template class functions

template<class T, class U>
StaticMap<T, U>::StaticMap(
    const int capacity,
    const T& fallback_key,
    const U& fallback_value) :
m_capacity(capacity),
m_fallback({fallback_key, fallback_value}),
m_size(0) {
    m_data = (pair*)malloc(sizeof(pair) * capacity);
    for (int i = 0; i < capacity; i++) {
        m_data[i].key   = fallback_key;
        m_data[i].value = fallback_value;
    }
}


template<class T, class U>
int StaticMap<T, U>::set(const T& key, const U& value) {
    // Check if specified key already exists
    int index = getIndex(key);
    if (!indexIsValid(index)) {
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


template<class T, class U>
const U& StaticMap<T, U>::get(const T& key) const {
    int index = getIndex(key);
    if (!indexIsValid(index))
        return m_fallback.value;
    return getByIndex(index);
}


template<class T, class U>
const U& StaticMap<T, U>::getByIndex(const int index) const {
    if (!indexIsValid(index))
        return m_fallback.value;
    return m_data[index].value;
}


template<class T, class U>
const T& StaticMap<T, U>::getKeyByIndex(const int index) const {
    if (!indexIsValid(index))
        return m_fallback.key;
    return m_data[index].key;
}


template<class T, class U>
bool StaticMap<T, U>::has(const U& value) const {
    for (const pair* it = begin(); it < end(); it++)
        if (it->value == value)
            return true;
    return false;
}


template<class T, class U>
bool StaticMap<T, U>::hasKey(const T& key) const {
    for (const pair* it = begin(); it < end(); it++)
        if (it->key == key)
            return true;
    return false;
}


template<class T, class U>
int StaticMap<T, U>::getIndex(const T& key) const {
    for (int i = 0; i < size(); i++)
        if (m_data[i].key == key)
            return i;
    return -1;
}


template<class T, class U>
void StaticMap<T, U>::clear() {
    m_size = 0;
}


template<class T, class U>
void StaticMap<T, U>::dump(Stream* const stream, const int indent) const {
    char line[80] = {0};
    int i = 0;
    for (auto it = begin(); it < end(); it++) {
        snprintf_P(line, sizeof(line), PSTR("[%03d]  "), i++);
        for (int j = 0; j < indent; j++)
            stream->print(' ');
        stream->print(line);
        stream->print(it->key);
        stream->print(F(" -> "));
        stream->println(it->value);
    }

    snprintf_P(line, sizeof(line), PSTR("Size: key=%zuB, value=%zuB, total=%zuB, %d/%d items allocated at: %p"),
        sizeof(T),
        sizeof(U),
        storageSize(),
        size(),
        capacity(),
        (void*)m_data);
    for (int j = 0; j < indent; j++)
        stream->print(' ');
    stream->println(line);
}


template<class T, class U>
const typename StaticMap<T, U>::pair* StaticMap<T, U>::find(const T& key) const {
    for (const pair* it = begin(); it < end(); it++)
        if (it->key == key)
            return it;
    return end();
}


#endif  // SRC_CONTAINER_MAP_H_
