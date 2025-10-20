#!/usr/bin/env bash

# Проверка аргументов
if [ -z "$1" ]; then
  echo "Не передан путь к файлам swagger"
  exit 1
else
  OPENAPIV2_PATH="$1"
fi

if [ -z "$2" ]; then
  echo "не передан title для объединенного swagger файла"
  exit 1
else
  OPENAPIV2_TITLE="$2"
fi

if [ -z "$3" ]; then
  echo "не передана версия для объединенного swagger файла"
  exit 1
else
  OPENAPIV2_VERSION="$3"
fi

TARGET_DIR="build/generated/${OPENAPIV2_PATH}"

# Проверка существования директории
if [ ! -d "$TARGET_DIR" ]; then
  echo "Директория $TARGET_DIR не существует"
  exit 1
fi

# Проверка пуста ли директория
if [ -z "$(ls -A "$TARGET_DIR")" ]; then
  echo "Указанная директория пустая"
  exit 1
fi

cd $TARGET_DIR

# Формируется начальный JSON
echo "Начальный JSON:"
echo "{\"swagger\": \"2.0\", \"info\": {\"title\": \"$OPENAPIV2_TITLE\", \"version\": \"$OPENAPIV2_VERSION\"}, \"tags\": [], \"schemes\": [], \"consumes\": [], \"produces\": [], \"paths\": {}, \"definitions\": {}}" > openapi.swagger.json

echo "Поиск всех swagger.json:"
find . -type f -name '*.swagger.json'

jq -s '
  def deepmerge(a; b):
    if (a | type) == "object" and (b | type) == "object" then
      reduce (a | keys_unsorted[]) as $key
        ({}; . + { "\($key)": if ($key | in(b)) then deepmerge(a[$key]; b[$key]) else a[$key] end })
      + reduce (b | keys_unsorted[]) as $key
        ({}; if ($key | in(a)) then . else . + { ($key): b[$key] } end)
    elif (a | type) == "array" and (b | type) == "array" then
      (a + b) | unique
    else b end;
  reduce .[] as $item
    ({}; deepmerge(.; $item))
' $(find . -type f -name '*.swagger.json' -exec printf "%s " {} +) > openapi.swagger.json