import groovy.io.FileType
import com.google.gson.*
import groovy.json.JsonSlurper

// =======================================================================
// Функция глубокого слияния (та же, что и раньше)
// =======================================================================
/**
 * Рекурсивно сливает два Map.
 * @param map1 Базовый Map.
 * @param map2 Map, который "накладывается" сверху.
 * @return Новый, объединенный Map.
 */
def deepMerge(Map map1, Map map2) {
    def result = new HashMap<>(map1)
    map2.each { key, value ->
        if (result.containsKey(key) && result[key] instanceof Map && value instanceof Map) {
            result[key] = deepMerge(result[key] as Map, value as Map)
        } else if (result.containsKey(key) && result[key] instanceof List && value instanceof List) {
            result[key] = result[key] + value.findAll {!result[key].contains(it)}
        } else {
            result[key] = value
        }
    }
    return result
}

def directory = System.getProperty("openapiv2.files.path")
def resultFilePath = System.getProperty("openapiv2.merged.file")
def mergedSwaggerInfoName = System.getProperty("openapiv2.merged.title")
def mergedSwaggerInfoVersion = System.getProperty("openapiv2.merged.version")

// 1. Указываем стартовую директорию (точка означает текущую директорию)
def startDir = new File(directory)

// 2. Создаем список для хранения найденных файлов
def foundFiles = []

println "Поиск файлов *.swagger.json в директории: ${startDir.absolutePath}"
println "--------------------------------------------------------"

// 3. Рекурсивно обходим все ФАЙЛЫ
// FileType.FILES говорит, что нас интересуют только файлы, а не папки
startDir.eachFileRecurse(FileType.FILES) { file ->
    // 4. Проверяем, заканчивается ли имя файла на ".swagger.json"
    if (file.name.endsWith('.swagger.json')) {
        println "  [Найден] -> ${file.path}"
        // Добавляем найденный файл в наш список
        foundFiles << file
    }
}

println "--------------------------------------------------------"

// 5. Выводим итоговый результат
if (foundFiles) {
    println "Найдено всего файлов: ${foundFiles.size()}"
    println "Полные пути:"
    def slurper = new JsonSlurper()
    def resultMergedMap = [:]
    foundFiles.eachWithIndex { file, index ->
        println "  ${index + 1}. ${file.absolutePath}"


// --- 2. Парсим JSON в Groovy Map с помощью JsonSlurper ---
        if (file.text.isEmpty()) {
            println "${file.absolutePath} пустой. Пропускаем его слияние"
        } else {
            def map2 = slurper.parseText(file.text)

// --- 3. Выполняем слияние ---
            def mergedMap = deepMerge(resultMergedMap, map2)

// --- 4. Выводим результат в виде красивой JSON-строки ---
            resultMergedMap = mergedMap
        }
    }

    resultMergedMap["info"] = ["title": mergedSwaggerInfoName, "version": mergedSwaggerInfoVersion]

// Получаем компактную JSON-строку без экранирования
    def unescapedJson = new GsonBuilder()
            .setPrettyPrinting()
            .create()
            .toJson(resultMergedMap)


// 2. Создаем объект файла. Groovy использует стандартный java.io.File
    def outputFile = new File(resultFilePath)

// 3. Записываем контент в файл
    outputFile.write(unescapedJson, 'UTF-8')
} else {
    println "Файлы с именем *.swagger.json не найдены."
}
