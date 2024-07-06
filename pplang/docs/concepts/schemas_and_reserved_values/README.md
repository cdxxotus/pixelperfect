# Intro

When interpreting value, pplang can take it as it, or as schema

## Schemas

They are interpreted by pplang as a set of instruction to retrieve the expected output.

Operators and compilers can face such a situation. They are free to customize their interpretation of a schema.

pplang compiler actually excel at turning regular objects into schema that can be interpreted with extreme granularity.

The pplang/hard/reserved file contains unicode characters that are tied to the own existence of the schema.

## Reserved values

```
$ indicates next char point to a schema
[ indicates we are defining a list/array and next char point to its type
] indicates we completed the definition of a list/array
| indicates we completed the definition of a value and start defining another one
, indicates we completed the definition of an abject and we start defining another one
- indicates next char point to a state
* indicates next value is of 'compiled with pplang' type
+ indicates next char point to a constant
{ indicates we are defining an object and next char point to its type
} indicates we completed the definition of an object
( indicates next chars until ')' is a raw value
) indicates we completed the definition of a raw value
@ indicates next char is the key of the dictionary at pointer @
~ indicates we are defining a number starting at next char until next non digit char
```
