#ifndef SRC_MAP_H_
#define SRC_MAP_H_

// Simple map helper class
template<class T_KEY, class T_VALUE>
class Map {
 public:
    // Definition of template data structure
    struct key_value { T_KEY key; T_VALUE value; };

    // Constructor for an empty set
    Map(T_KEY fallback_key, T_VALUE fallback_value):
    m_fallback_key(fallback_key),
    m_fallback_value(fallback_value),
    m_storage(0),
    m_items(0)
    {}

    // Destructor for storage cleanup
    ~Map() {
        if (m_storage)
            free(m_storage);
    }

    // Adds a key-value pair to the set (resizes the allocated memory)
    bool addPair(T_KEY key, T_VALUE value) {
        int index = getIndex(key);
        if (index < 0) {
            size_t new_size = (m_items + 1) * sizeof(key_value);
            void* new_pointer = realloc(m_storage, new_size);
            if (!new_pointer)
                return false;
            m_storage = (key_value*)new_pointer;
            index = m_items++;
        }
        m_storage[index].key = key;
        m_storage[index].value = value;

        return true;
    }

    // Removes a specified key-value pair from the set (resizes the allocated memory)
    bool removePair(T_KEY key) {
        int index = getIndex(key);
        if (index < 0 || index >= m_items)
            return false;

        return removePairByIndex(index);
    }

    // Removes a specified data set identified by its index from the set (resizes the allocated memory)
    bool removePairByIndex(int index) {
        if (index < 0 || index >= m_items)
            return false;

        int j = 0;
        for (int i = 0; i < size(); i++)
            if (i != index)
                m_storage[j++] = m_storage[i];

        size_t new_size = (m_items - 1) * sizeof(key_value);
        void* new_pointer = realloc(m_storage, new_size);
        if (!new_pointer)
            return false;
        m_storage = (key_value*)new_pointer;
        m_items--;

        return true;
    }

    // Fetches the value of an element identified by its key
    T_VALUE getValue(T_KEY key) const {
        int index = getIndex(key);
        if (index < 0 || index >= m_items)
            return m_fallback_value;

        return m_storage[index].value;
    }

    // Fetches the numerical index (=array position) of an element identified by its key
    int getIndex(T_KEY key) const {
        for (int i = 0; i < size(); i++)
            if (m_storage[i].key == key)
                return i;
        return -1;
    }

    // Fetches the key of an element identified by its index
    T_KEY getKeyByIndex(int index) const {
        if (index < 0 || index >= m_items)
            return m_fallback_key;

        return m_storage[index].key;
    }

    // Fetches the value of an element identified by its index
    T_VALUE getValueByIndex(int index) const {
        if (index < 0 || index >= m_items)
            return m_fallback_value;

        return m_storage[index].value;
    }

    // Retreives the number of elements currently holded by the map
    int size() const {
        return m_items;
    }

    // Retreives the total storage size of the map content
    size_t storageSize() const {
        return m_items * sizeof(key_value);
    }

    // Checks if a specific key is set
    bool hasKey(T_KEY key) const {
        for (int i = 0; i < size(); i++)
            if (m_storage[i].key == key)
                return true;
        return false;
    }

    // Checks if a specific value is set
    bool hasValue(T_VALUE value) const {
        for (int i = 0; i < size(); i++)
            if (m_storage[i].value == value)
                return true;
        return false;
    }

    // Dumps the map's contents to a stream object
    void dumps(Stream* const stream) {
        char line[80] = {0};
        for (int i = 0; i < size(); i++) {
            sprintf_P(line, PSTR("[%02d]  "), i);
            stream->print(line);
            stream->print(getKeyByIndex(i));
            stream->print(F(" -> "));
            stream->println(getValueByIndex(i));
        }

        sprintf_P(line, PSTR("Key/value/total size: %d/%d/%dB, %d entries allocated at %06p"),
            sizeof(T_KEY),
            sizeof(T_VALUE),
            size() * sizeof(key_value),
            m_items,
            m_storage);
        stream->println(line);
    }

 private:
    const T_KEY     m_fallback_key;
    const T_VALUE   m_fallback_value;
    key_value*      m_storage;
    int             m_items;
};

#endif  // SRC_MAP_H_
