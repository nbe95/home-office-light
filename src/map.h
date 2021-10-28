#ifndef _MAP_H_
#define _MAP_H_

// Simple map helper class
template<class T_KEY, class T_VALUE>
class Map
{
public:
    // Definition of template data structure
    struct key_value { T_KEY key; T_VALUE value; };

    // Constructor for an empty set
    Map(): m_storage(0), m_items(0) {};

    // Adds a key-value pair to the set (resizes the allocated memory)
    bool addPair(T_KEY key, T_VALUE value)
    {
        int index = getIndex(key);
        if (index < 0)
        {
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
    };

    // Removes a specified key-value pair from the set (resizes the allocated memory)
    bool removePair(T_KEY key)
    {
        int index = getIndex(key);
        if (index < 0)
            return false;

        int j = 0;
        for (int i = 0; i < getSize(); i++)
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
    bool getValue(T_KEY key, T_VALUE* target) const
    {
        int index = getIndex(key);
        if (index < 0 || index >= m_items)
            return false;

        *target = m_storage[index].value;
        return true;
    }

    // Fetches the numerical index (=array position) of an element identified by its key
    int getIndex(T_KEY key) const
    {
        for (int i = 0; i < getSize(); i++)
            if (m_storage[i].key == key)
                return i;
        return -1;
    }

    // Fetches the key of an element identified by its index
    bool getKeyByIndex(int index, T_KEY* target) const
    {
        if (index < 0 || index >= m_items)
            return false;

        *target = m_storage[index].key;
        return true;
    }

    // Fetches the value of an element identified by its index
    bool getValueByIndex(int index, T_VALUE* target) const
    {
        if (index < 0 || index >= m_items)
            return false;

        *target = m_storage[index].value;
        return true;
    }

    // Retreives the number of elements currently holded by the map
    int getSize() const
    {
        return m_items;
    }

private:
    key_value* m_storage;
    int m_items;
};

#endif /* _MAP_H_ */