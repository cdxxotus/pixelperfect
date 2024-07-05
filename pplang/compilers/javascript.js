const fs = require("fs")
const path = require("path")
const logging = require("loglevel")
const { performance } = require("perf_hooks")

// Configure logging
logging.setLevel("debug")

// Extend the String prototype with a replaceAll method
String.prototype.replaceAll = function (replacements) {
  let result = this
  for (const [search, replacement] of Object.entries(replacements)) {
    // Replace all occurrences of the search string with the replacement string
    let searchPos = result.indexOf(search)
    while (searchPos !== -1) {
      result =
        result.substring(0, searchPos) +
        replacement +
        result.substring(searchPos + search.length)
      searchPos = result.indexOf(search, searchPos + replacement.length)
    }
  }
  return result
}

// Use a dictionary to store pointers
const pointersNames = {}
const unicodeMap = []
const reservedChars = new Set()
const unicodeToIndex = {}

// Function to load reserved characters
function loadReservedChars(filename) {
  try {
    const data = fs.readFileSync(filename, "utf-8")
    for (const char of data.trim()) {
      reservedChars.add(char)
    }
  } catch (error) {
    logging.error(`Reserved characters file not found: ${filename}`)
  }
}

// Function to load unicode map
function loadUnicodeMap(filename) {
  try {
    const data = fs.readFileSync(filename, "utf-8")
    unicodeMap.push(...data.trim())
    unicodeMap.forEach((char, idx) => {
      unicodeToIndex[char] = idx
    })
  } catch (error) {
    logging.error(`Unicode map file not found: ${filename}`)
  }
}

// Load reserved characters and unicode map
loadReservedChars("pplang/hard/reserved")
loadUnicodeMap("pplang/hard/unicodes")

// Function to ensure list size
function ensureSize(lst, index) {
  while (lst.length <= index) {
    lst.push(null)
  }
}

// Function to get dictionary
function getDictionary(pointer) {
  const dictionary = {}
  const dictionaryPixels = []
  const seenPixels = new Set()
  try {
    const data = fs
      .readFileSync(`pplang/pointers/${pointer}`, "utf-8")
      .split("\n")
    data.forEach((line) => {
      if (line.trim()) {
        const pixel = line[0]
        const human = line.slice(1).trim()
        if (seenPixels.has(pixel)) {
          logging.warn(
            `Duplicate Unicode found: ${pixel}. Skipping entry: ${human}`
          )
        } else {
          dictionary[human] = pixel
          dictionaryPixels.push(pixel)
          seenPixels.add(pixel)
        }
      }
    })
    logging.debug(`Dictionary: ${JSON.stringify(dictionary)}`)
    logging.debug(`Dictionary Pixels: ${dictionaryPixels}`)
    return [dictionary, dictionaryPixels]
  } catch (error) {
    logging.error(`Pointer file not found: ${pointer}`)
    return [{}, []]
  }
}

// Function to get pointer names
function getPointerNames(pointer) {
  if (pointersNames[pointer]) {
    return pointersNames[pointer]
  }
  const selfPointersNames = []
  try {
    const data = fs
      .readFileSync(`pplang/pointers/${pointer}`, "utf-8")
      .split("\n")
    data.forEach((line) => {
      line = line.trim()
      if (line) {
        const match = line.match(/(\d+)(.+)/)
        if (match) {
          const index = parseInt(match[1])
          const value = match[2].trim()
          ensureSize(selfPointersNames, index)
          selfPointersNames[index] = value
        }
      }
    })
    pointersNames[pointer] = selfPointersNames
    return selfPointersNames
  } catch (error) {
    logging.error(`Pointer file not found: ${pointer}`)
    return []
  }
}

// Function to parse schema
function parseSchema(schema) {
  logging.debug(`parsechemabefore:${schema}`)
  let formattedString = schema.replaceAll({
    "{": '{"',
    "}": '"}',
    ":": '": "',
    ",": '", "',
  })
  logging.debug(`formatted_string:${formattedString}`)
  if (formattedString[0] === "[" || formattedString[0] === "{") {
    try {
      return JSON.parse(formattedString)
    } catch (error) {
      logging.error(`Failed to parse schema: ${error}`)
      return {}
    }
  } else {
    return formattedString
  }
}

// Function to get pointer position
function getPointerPos(pointersPos, pointer, name) {
  if (!pointersPos[pointer]) {
    pointersPos[pointer] = {}
  }
  if (pointersPos[pointer][name]) {
    return pointersPos[pointer][name]
  }
  try {
    const data = fs
      .readFileSync(`pplang/pointers/${pointer}`, "utf-8")
      .split("\n")
    data.forEach((line) => {
      line = line.trim()
      if (line) {
        const match = line.match(/(\d+)(.+)/)
        if (match) {
          const index = parseInt(match[1])
          const value = match[2].trim()
          if (value === name) {
            pointersPos[pointer][name] = index
            return index
          }
        }
      }
    })
  } catch (error) {
    logging.error(`Pointer file not found: ${pointer}`)
  }
  return pointersPos[pointer][name]
}

// Function to translate with priority
function translateWithPriority(bigString, translations) {
  const words = bigString.split(/\s+/)
  logging.debug(`Split words: ${words}`)
  const sortedKeys = Object.keys(translations).sort(
    (a, b) => b.length - a.length
  )
  let encoded = ""
  for (const word of words) {
    let matched = false
    for (const key of sortedKeys) {
      if (word === key) {
        logging.debug(`Translating: ${word} -> ${translations[key]}`)
        encoded += `${translations[key].trim()}¡`
        matched = true
        break
      }
    }
    if (!matched) {
      encoded += `${word.trim()}¡`
    }
  }
  return encoded
}

// Function to process object
function processObject(schema, obj) {
  const selfPointersPos = {}
  logging.debug(
    `process_object:schema,obj::${schema.constructor.name}:${JSON.stringify(
      obj
    )}`
  )
  if (Array.isArray(schema)) {
    const compiledResult = []
    obj.forEach((item) => {
      const compiledItem = new Array(Object.keys(schema[0]).length).fill(null)
      let idx = 0
      for (const [key, value] of Object.entries(schema[0])) {
        if (value in item) {
          if (idx === 0) {
            selfPointersPos[key] = {}
          }
          const itemValue = item[value]
          const keyPointerIndex = getPointerPos(selfPointersPos, key, itemValue)
          compiledItem[idx] = keyPointerIndex
          idx += 1
        }
      }
      compiledResult.push(compiledItem)
    })
    return compiledResult
  } else if (typeof schema === "object") {
    const compiledItem = new Array(Object.keys(schema).length).fill(null)
    let idx = 0
    for (const [key, value] of Object.entries(schema)) {
      let forcer_lentree = value === "@"
      if (forcer_lentree || value in obj || value[0] === "+") {
        if (idx === 0) {
          selfPointersPos[key] = {}
        }
        let itemValue
        if (value[0] === "+") {
          const constNames = getPointerNames("+")
          const itemKey = constNames[parseInt(value.slice(1))]
          itemValue = obj[itemKey]
        } else {
          itemValue = obj[value]
        }
        if (key === "*") {
          compiledItem[idx] = `*(${itemValue})`
        } else if (key[0] === "+") {
          compiledItem[idx] = `(${itemValue})`
        } else if (key[0] === "@") {
          const lightToShadow = itemValue.replace(/ /g, "¦¦")
          compiledItem[idx] = `(${lightToShadow})`
        } else {
          const keyPointerIndex = getPointerPos(selfPointersPos, key, itemValue)
          compiledItem[idx] = keyPointerIndex
        }
        idx += 1
      }
    }
    return compiledItem
  } else if (schema === "@") {
    const [dictionary, dictionaryPixels] = getDictionary(schema)
    const shadowspaces = obj.replace(/ /g, "​")
    const translated = translateWithPriority(shadowspaces, dictionary)
    return translated
  }
}

// Function to get reverse dictionary
function getReverseDictionary(dictionary) {
  if (typeof dictionary === "object") {
    const reverseDict = Object.fromEntries(
      Object.entries(dictionary).map(([k, v]) => [v, k])
    )
    logging.debug(`Reverse Dictionary: ${JSON.stringify(reverseDict)}`)
    return reverseDict
  } else {
    throw new Error("Input is not a dictionary")
  }
}

// Function to reverse translate with priority
function reverseTranslateWithPriority(encodedString, translations) {
  const reverseTranslations = Object.fromEntries(
    Object.entries(translations).map(([k, v]) => [v, k])
  )
  const words = encodedString.split("*%*")
  const sortedKeys = Object.keys(reverseTranslations).sort(
    (a, b) => b.length - a.length
  )
  const decodedWords = []
  for (const word of words) {
    let matched = false
    for (const key of sortedKeys) {
      if (word === key) {
        logging.debug(
          `Reverse Translating: ${word} -> ${reverseTranslations[key]}`
        )
        decodedWords.push(reverseTranslations[key])
        matched = true
        break
      }
    }
    if (!matched) {
      decodedWords.push(word)
    }
  }
  return decodedWords.join(" ")
}

// Function to reverse compiled string
function reverseCompiledString(compiledString, pointer) {
  const [dictionary, dictionaryPixels] = getDictionary(pointer)
  return reverseTranslateWithPriority(compiledString, dictionary)
}

// Function to get next character
function* nextChar(compiledStr) {
  for (const char of compiledStr) {
    yield char
  }
}

// Function to jump to next schema
function jumpToNextSchema(charGen) {
  let substring = ""
  for (const char of charGen) {
    if (char === "$") {
      return substring
    }
    substring += char
  }
  return substring
}

// Function to compile
function compile(pointer, obj) {
  const startTime = performance.now()

  const schemaPointersNames = getPointerNames(pointer)
  const schemaPointerPos = getPointerPos({}, "=", pointer)
  const rawSchema = schemaPointersNames[0] || ""
  const schema = parseSchema(rawSchema)
  // console.log({ schema:JSON.stringify(schema) })

  logging.debug(`schema:${JSON.stringify(schema)}`)
  logging.debug(`obj:${JSON.stringify(obj)}`)

  const processedObj = processObject(schema, obj)
  let stringifiedObj = JSON.stringify(processedObj)
  stringifiedObj = stringifiedObj.replace(/\\'/g, "'")

  if (stringifiedObj[0] === "[" && stringifiedObj[1] !== "[") {
    stringifiedObj = replaceAtIndex(stringifiedObj, 0, "{")
    stringifiedObj = replaceAtIndex(
      stringifiedObj,
      stringifiedObj.length - 1,
      "}"
    )
  }

  let compiledResult = `$${schemaPointerPos}${stringifiedObj}`.replaceAll({
    "\\\\": "\\",
    "'*": "*",
    "'`": "",
    "`'": "",
    '"': "",
    " ": "",
    null: "-",
    "],[": "|",
    "[[": "[",
    "]]": "]",
    ")'": ")",
    "'(": "(",
  })

  const parts = compiledResult.split(/(?<!\\)(\d+\.\d+|\d+|.)/)
  const unicodeResult = parts
    .map((part) => (part.match(/^\d+$/) ? convertNum(part) : part))
    .join("")

  const endTime = performance.now()
  logging.warn(`Compilation time: ${(endTime - startTime).toFixed(6)} seconds`)

  return [unicodeResult, endTime - startTime]
}

// Function to uncompile
function uncompile(compiledStr) {
  const startTime = performance.now()

  const shadowToLightStr = compiledStr.replaceAll({
    "¦¦": " ",
  })

  const charGen = nextChar(shadowToLightStr)

  let decodedData = ""
  let isEscaped = false
  let schema = []
  let parentSchema = []
  let firstSchema = []
  let currentOperation = ""
  let xSchema = 0
  let xObject = 0
  let decodingUpTo = ""
  let inNestedBuild = false
  let characters = ""

  for (const char of charGen) {
    characters += char
    console.log({
      currentOperation,
      // // xObject,
      // // inNestedBuild,
      // decodedData,
      // schema,
      // characters,
    })
    decodingUpTo += char
    if (char === "\\" && !isEscaped) {
      isEscaped = true
    } else if (char === "{" && !isEscaped) {
      xObject = 0
      decodedData += char
      currentOperation = "{"
    } else if (char === "}" && !isEscaped) {
      decodedData += char
    } else if (char === "(" && !isEscaped) {
      if (!inNestedBuild) {
        const key = Object.keys(schema[0])[xObject]
        if (schema[0][key][0] === "+") {
          const pointerName =
            getPointerNames("+")[parseInt(schema[0][key].slice(1))]
          decodedData += `"${pointerName}":"`
        } else {
          decodedData += `"${schema[0][key]}":"`
        }
        currentOperation = "("
      }
    } else if (char === ")" && !isEscaped) {
      if (inNestedBuild) {
        schema = parentSchema
        inNestedBuild = false
      } else {
        decodedData += `"`
      }
    } else if (char === "$" && !isEscaped) {
      xObject = 0
      currentOperation = "$"
    } else if (char === "[" && !isEscaped) {
      xObject = 0
      decodedData += char
      currentOperation = "[{"
    } else if (char === "," && !isEscaped) {
      decodedData += char
      xObject += 1
    } else if (char === "]" && !isEscaped) {
      if (currentOperation === "{") {
        decodedData += `}}${char}`
      } else {
        decodedData += char
      }
      currentOperation = "{"
      xObject = 0
    } else if (char === "|" && !isEscaped) {
      if (currentOperation === "{") {
        decodedData += "},{"
      } else {
        decodedData += "],["
      }
      xObject = 0
      currentOperation = "{"
    } else {
      isEscaped = false
      const pos = parseInt(unicodeToIndex[char] || -1)

      if (currentOperation === "$") {
        const schemaListPointersNames = getPointerNames("=")
        const schemaName = schemaListPointersNames[pos]
        const rawSchema = getPointerNames(schemaName)[0]
        const unknownSchema = parseSchema(rawSchema)
        parentSchema = schema
        if (!Array.isArray(unknownSchema)) {
          schema = [unknownSchema]
        } else {
          schema = unknownSchema
        }
        if (firstSchema.length === 0) {
          ensureSize(firstSchema, 0)
          firstSchema[0] = schema
        }
        if (schema[0] === "@") {
          currentOperation = "@"
          decodedData += `"`
        } else {
          currentOperation = ""
        }
      } else if (currentOperation === "(") {
        decodedData += char
      } else if (currentOperation === "[{") {
        const key = Object.keys(schema[0])[xObject]
        if (char === "-") {
          decodedData += `{"${schema[0][key]}":null`
        } else {
          const pointerNames = getPointerNames(key)
          const pointerName = pointerNames[pos] || "null"
          decodedData += `{"${schema[0][key]}":"${pointerName}"`
        }
        currentOperation = "{"
      } else if (currentOperation === "{") {
        const key = Object.keys(schema[0])[xObject]
        // console.log({
        //   key,
        //   schema: schema[0],
        //   keys: Object.keys(schema[0]),
        //   xObject,
        // })
        if (char === "-") {
          decodedData += `"${schema[0][key]}":null`
        } else if (char === "*") {
          inNestedBuild = true
          decodedData += `"${schema[0][key]}":`
        } else {
          const pointerNames = getPointerNames(key)
          const pointerName = pointerNames[pos] || "null"
          decodedData += `"${schema[0][key]}":"${pointerName}"`
        }
      } else if (currentOperation === "@") {
        const substring = jumpToNextSchema(charGen)
        const translation = reverseCompiledString(char + substring, "@")
        decodedData += translation
      }
    }
  }

  decodedData = decodedData

  console.log({ decodedData })

  let compiledResults = decodedData

  if (typeof firstSchema[0] === "object" || Array.isArray(firstSchema[0])) {
    try {
      compiledResults = JSON.parse(decodedData)
    } catch (error) {
      logging.error(`Failed to parse decoded data: ${error}`)
      return [null, 0]
    }
  }

  const endTime = performance.now()
  logging.warn(
    `Uncompilation time: ${(endTime - startTime).toFixed(6)} seconds`
  )

  return [compiledResults, endTime - startTime]
}

// Function to calculate compression rate
function calculateCompressionRate(original, compiled) {
  const originalSize = Buffer.byteLength(original, "utf-8")
  const compiledSize = Buffer.byteLength(compiled, "utf-8")
  const compressionRate = (1 - compiledSize / originalSize) * 100
  return compressionRate
}

// Function to convert number
function convertNum(num) {
  if (num.match(/^\d+$/)) {
    const index = parseInt(num)
    if (index >= 0 && index < unicodeMap.length) {
      const unicodeChar = unicodeMap[index]
      if (reservedChars.has(unicodeChar)) {
        return `\\${unicodeChar}`
      }
      return unicodeChar
    }
  }
  return num
}

// Function to replace at index
function replaceAtIndex(s, index, replacement) {
  if (index < 0 || index >= s.length) {
    throw new Error("Index out of range")
  }
  return s.slice(0, index) + replacement + s.slice(index + 1)
}

// Example usage
// const pointer = "ui_color_palette_schema"
// const data = [
//   { color: "Beige", type: "Secondary color", score: 0.9999566078186035 },
//   {
//     color: "Cyan",
//     type: "Notification highlight color",
//     score: 0.9999328851699829,
//   },
//   { color: "Pink", type: "Accent color", score: 0.9999185800552368 },
//   { color: "AliceBlue", type: "Text color", score: 0.999894380569458 },
//   { color: "WhiteSmoke", type: "Border color", score: 0.9998866319656372 },
//   { color: "Purple", type: "Highlight color", score: 0.9998842477798462 },
//   { color: "Azure", type: "Main color", score: 0.9998782873153687 },
//   { color: "AntiqueWhite", type: "Alert color", score: 0.9998581409454346 },
//   {
//     color: "DarkGray",
//     type: "Subtle background color",
//     score: 0.9996941089630127,
//   },
// ]

// const dataColorPaletResponse = {
//   color_palet: `$\\$[¾,${'"'}|ʹ,&|ャ,%|-,#|-,\\(|両,\\$|~,!|-,\\)|-,']`,
//   inference_time: 2.1053810119628906,
// }

// const dataOsDescription = {
//   os_home_screen_description: "qsdfqsdf qs qsdf qsdf qsdf qsd qq qsf",
//   inference_time: 1.343,
// }

// const dataString = `
// Vous pouvez partager un article en cliquant sur les icônes de partage en haut à droite de celui-ci.
// La reproduction totale ou partielle d’un article, sans l’autorisation écrite et préalable du Monde, est strictement interdite.
// Pour plus d’informations, consultez nos conditions générales de vente.
// Pour toute demande d’autorisation, contactez syndication@lemonde.fr.
// En tant qu’abonné, vous pouvez offrir jusqu’à cinq articles par mois à l’un de vos proches grâce à la fonctionnalité « Offrir un article ».

// https://www.lemonde.fr/politique/live/2024/07/04/en-direct-legislatives-2024-plus-de-3-1-millions-de-procurations-sur-l-ensemble-des-scrutins_6245747_823448.html

// Le préfet de police de Paris, Laurent Nuñez, va interdire une manifestation du collectif Action antifasciste Paris-Banlieue prévue dimanche devant l’Assemblée nationale à la clôture du second tour des législatives, a rapporté jeudi soir à l’Agence France-Presse une source policière.

// Ce collectif a appelé dans un post sur X à un rassemblement « dimanche à 20 h devant l’Assemblée nationale quelle que soit l’issue » du scrutin. « Aujourd’hui plus que jamais, faisons bloc par tous les moyens contre l’extrême droite et ses alliés », a-t-il fait valoir. Sur les réseaux sociaux, le collectif a lancé un appel à « converger vers l’Assemblée nationale ».

// Le ministre de l’intérieur, Gérald Darmanin, a annoncé jeudi que « 30 000 policiers et gendarmes, dont 5 000 à Paris et sa banlieue » seraient mobilisés dimanche soir pour le second tour du scrutin législatif anticipé. Les services de renseignement considèrent, selon une source policière, qu’il existe « de réels risques de troubles à l’ordre public après le second tour avec à la fois des rassemblements qui pourraient donner lieu à des incidents mais aussi des risques d’affrontements entre des groupes antagonistes ».
// `

// const [compiledData, compileTime] = compile(pointer, data)
// console.log("Compiled Data:")
// console.log(compiledData)

// const [uncompiledData, uncompileTime] = uncompile(compiledData)
// console.log("Uncompiled Data:")
// console.log(uncompiledData)

// const [compiledColorPaletResponseData, __] = compile(
//   "ui_color_palette_response",
//   dataColorPaletResponse
// )
// console.log("Compiled ColorPaletResponse Data:")
// console.log(compiledColorPaletResponseData)

// const [uncompiledColorPaletResponseData, _] = uncompile(
//   compiledColorPaletResponseData
// )
// console.log("Uncompiled ColorPaletResponse Data:")
// console.log(uncompiledColorPaletResponseData)

// const [compiledDataOs, compileTimeOs] = compile(
//   "os_home_screen_description_response",
//   dataOsDescription
// )
// console.log("Compiled Data_os:")
// console.log(compiledDataOs)

// const [uncompiledDataOs, uncompileTimeOs] = uncompile(compiledDataOs)
// console.log("Uncompiled Data_os:")
// console.log(uncompiledDataOs)

// const [compiledString, compileStringTime] = compile("string", dataString)
// console.log("Compiled String Data:")
// console.log(compiledString)
// console.log("Original String Data:", dataString)

// const [uncompiledString, uncompileStringTime] = uncompile(compiledString)
// console.log("Uncompiled String Data:")
// console.log(uncompiledString)

// // Calculate compression rates
// const compressionRateData = calculateCompressionRate(
//   JSON.stringify(uncompiledData),
//   compiledData
// )
// const compressionRateColorPaletResponse = calculateCompressionRate(
//   JSON.stringify(uncompiledColorPaletResponseData),
//   compiledColorPaletResponseData
// )
// const compressionRateString = calculateCompressionRate(
//   JSON.stringify(uncompiledString),
//   compiledString
// )

// console.log(`Compression Rate (data): ${compressionRateData.toFixed(2)}%`)
// console.log(
//   `Compression Rate (color_palet_response): ${compressionRateColorPaletResponse.toFixed(
//     2
//   )}%`
// )
// console.log(`Compression Rate (string): ${compressionRateString.toFixed(2)}%`)

// console.log(`Compilation time for data: ${compileTime.toFixed(6)} seconds`)
// console.log(`Uncompilation time for data: ${uncompileTime.toFixed(6)} seconds`)
// console.log(
//   `Compilation time for string: ${compileStringTime.toFixed(6)} seconds`
// )
// console.log(
//   `Uncompilation time for string: ${uncompileStringTime.toFixed(6)} seconds`
// )

module.exports = {
  uncompile,
  compile,
}
