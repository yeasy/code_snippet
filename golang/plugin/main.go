package main

import (
    "fmt"
    "plugin"
)

func main() {
    // Load the plugin and lookup the public methods
    p, err := plugin.Open("./plugin.so")
    if err != nil {
        panic(err)
    }

    // Lookup return a Symbol, need to convert to func type first
    value, err := p.Lookup("Value") //value is a local pointer to the Value
    if err != nil {
        panic(err)
    }

    addSymbol, err := p.Lookup("Add")
    if err != nil {
        panic(err)
    }
    add := addSymbol.(func(int, int) int)

    subSymbol, err := p.Lookup("Sub")
    if err != nil {
        panic(err)
    }
    sub := subSymbol.(func(int, int) int)

    getValueSymbol, err := p.Lookup("GetValue")
    if err != nil {
        panic(err)
    }
    getValue := getValueSymbol.(func() int)

    // Only this way will affect the plugin's Value variable
    *value.(*int) = 10
    fmt.Printf("value=%d, getValue=%d\n", value, getValue())

    value = add(1,2)
    fmt.Printf("value=%d, getValue=%d\n", value, getValue())

    value = sub(1,2)
    fmt.Printf("value=%d, getValue=%d\n", value, getValue())

}
