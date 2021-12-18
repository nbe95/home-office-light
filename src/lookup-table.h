#ifndef SRC_LOOKUP_TABLE_H_
#define SRC_LOOKUP_TABLE_H_

// Lookup table helper class
// Note: To prevent heap fragmentation, a LookupTable is a fixed size container!
// This is NOT a dynamically allocated data structure like a map.
template<class T_KEY, class T_VALUE, int SIZE = 1>
class LookupTable {
 public:
    // Default constructor
    LookupTable() :
    LookupTable(T_KEY(), T_VALUE()) {}

    // Constructor with special fallback values
    LookupTable(T_KEY fallback_key, T_VALUE fallback_value) :
    m_items(0),
    m_size(SIZE),
    m_fallback_key(fallback_key),
    m_fallback_value(fallback_value) {
        for (int i = 0; i < m_size; i++) {
            m_storage[i].key = fallback_key;
            m_storage[i].value = fallback_value;
        }
    }

    // Destructor for storage cleanup
    ~LookupTable() {}

    // Adds a key-value pair to the table or updates an existing one,
    // returns the corresponding/new index
    int set(const T_KEY key, const T_VALUE value) {
        // Check if specified key already exists
        int index = getIndex(key);
        if (index < 0) {
            // Don't do anything if table is already full
            if (items() >= size())
                return -1;

            // Use first empty item
            index = m_items++;
        }
        m_storage[index].key = key;
        m_storage[index].value = value;
        return index;
    }

    // Fetches the numerical index (=array position) of an element identified by its key
    int getIndex(T_KEY key) const {
        for (int i = 0; i < items(); i++)
            if (m_storage[i].key == key)
                return i;
        return -1;
    }

    // Fetches the value of an element identified by its key
    T_VALUE getValue(T_KEY key) const {
        return getValueByIndex(getIndex(key));
    }

    // Fetches the value of an element identified by its index
    T_VALUE getValueByIndex(int index) const {
        if (index < 0 || index >= items())
            return m_fallback_value;

        return m_storage[index].value;
    }

    // Fetches the key of an element identified by its index
    T_KEY getKeyByIndex(int index) const {
        if (index < 0 || index >= items())
            return m_fallback_key;

        return m_storage[index].key;
    }

    // Retreives the number of elements currently holded by the table
    int items() const {
        return m_items;
    }

    // Retreives the total number of elements the table can hold
    int size() const {
        return m_size;
    }

    // Retreives the total storage size of the map content
    size_t storageSize() const {
        return sizeof(data) * items();
    }

    // Checks if a specific key is set
    bool hasKey(T_KEY key) const {
        for (int i = 0; i < items(); i++)
            if (m_storage[i].key == key)
                return true;
        return false;
    }

    // Checks if a specific value is set
    bool hasValue(T_VALUE value) const {
        for (int i = 0; i < items(); i++)
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

        sprintf_P(line, PSTR("Key/value/total size: %d/%d/%dB, %d/%d items allocated at: %06p"),
            sizeof(T_KEY),
            sizeof(T_VALUE),
            sizeof(data) * items(),
            items(),
            size(),
            m_storage);
        stream->println(line);
    }

 private:
    // Definition of template data structure
    struct data {
        T_KEY key;
        T_VALUE value;
    };

    // Private members
    const T_KEY     m_fallback_key;
    const T_VALUE   m_fallback_value;
    data            m_storage[SIZE];
    const int       m_size;
    int             m_items;
};

#endif  // SRC_LOOKUP_TABLE_H_
