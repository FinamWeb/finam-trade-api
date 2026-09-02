# Выпуск Python SDK

Пакеты Python и Node.js используют одну версию и один GitHub Release. Этот
документ описывает настройку, специфичную для PyPI; общий чеклист релиза — в
[руководстве по выпуску SDK](../node/RELEASING.md).

## Разовая настройка

Workflow публикации использует
[доверенную публикацию PyPI](https://docs.pypi.org/trusted-publishers/) через
OIDC — API-токены в репозитории не хранятся. Это настраивается один раз на
каждый индекс (PyPI и TestPyPI) для проекта.

### 1. Проекты в PyPI

Проект `finam-sdk` уже существует в PyPI. Для TestPyPI создайте его первой
ручной загрузкой (с токеном на уровне аккаунта) **или** настройте «pending
publisher» до появления первого релиза.

Путь через pending publisher предпочтителен: он позволяет GitHub Action создать
проект при первой публикации, ни разу не используя API-токен:

- PyPI: <https://pypi.org/manage/account/publishing/> → *Add a pending publisher*
- TestPyPI: <https://test.pypi.org/manage/account/publishing/> → *Add a pending publisher*

Используйте эти значения для обоих индексов:

| Поле | Значение |
| --- | --- |
| PyPI project name | `finam-sdk` |
| Owner | `FinamWeb` |
| Repository name | `finam-trade-api` |
| Workflow filename | `publish_python.yml` |
| Environment | `pypi` (боевой) / `testpypi` (тестовый) |

### 2. Окружения GitHub

В репозитории GitHub откройте **Settings → Environments** и создайте два
окружения: `pypi` и `testpypi`.

Для `pypi` настоятельно рекомендуется:

- **Required reviewers** — хотя бы один мейнтейнер должен одобрить каждый запуск
  публикации. Это защита от случайных релизов (версии в PyPI неизменяемы).
- **Deployment branches** — только пуши тегов.

Для `testpypi` ревьюеры не нужны — пререлизы должны публиковаться без
церемоний.

## Выпуск релиза

### Пререлиз / прогон (публикуется в TestPyPI)

1. Поднимите оба SDK до одной пререлизной версии по
   [общему чеклисту](../node/RELEASING.md), например `2.20.0-rc.1`.
2. Обновите [CHANGELOG.md](CHANGELOG.md): перенесите пункты из `[Unreleased]`
   в новый раздел `[2.20.0-rc.1] — YYYY-MM-DD`.
3. Закоммитьте, запушьте, влейте в `main`.
4. Создайте GitHub Release с соответствующим «голым» тегом версии на `main`.
   Отметьте его как *Pre-release*.
5. Workflow `publish_python.yml` обнаружит пререлизный маркер в теге и
   опубликует в TestPyPI.
6. Проверьте в чистом venv:
   ```sh
   python -m venv /tmp/finam-verify && source /tmp/finam-verify/bin/activate
   pip install -i https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     finam-sdk==2.20.0rc1
   python -c "from finam_trade_api import FinamClient; print('ok')"
   ```
   `--extra-index-url` нужен, потому что TestPyPI не зеркалирует runtime-
   зависимости (grpcio, protobuf и т. д.).

### Финальный релиз (публикуется в PyPI)

1. Поднимите оба SDK до одной финальной версии по
   [общему чеклисту](../node/RELEASING.md).
2. Аналогично обновите [CHANGELOG.md](CHANGELOG.md) — финальный раздел.
3. Закоммитьте, запушьте, влейте в `main`.
4. Создайте GitHub Release с соответствующим «голым» тегом версии на `main`.
   **Не** отмечайте его как пререлиз.
5. Workflow обнаружит финальный тег, потребует одобрения окружения (по настройке
   `pypi`) и после одобрения опубликует в PyPI.
6. Проверьте:
   ```sh
   python -m venv /tmp/finam-verify && source /tmp/finam-verify/bin/activate
   pip install finam-sdk==2.19.1
   python -c "from finam_trade_api import FinamClient; print('ok')"
   ```

## Политика версий

Оба пакета следуют линии релизов Trade API и
[семантическому версионированию](https://semver.org/):

- **Major (X.0.0)** — несовместимые изменения публичного API или протокола.
- **Minor (X.Y.0)** — обратно совместимые RPC или возможности SDK.
- **Patch (X.Y.Z)** — исправления, рефакторинг и синхронизированные релизы
  пакетов.

## Устранение проблем

### «Tag does not match pyproject.toml version»

Задача `build` проверяет, что тег релиза (`2.19.1`) и версии обоих пакетов
совпадают. Если вы поставили тег до повышения версии: удалите релиз и тег,
поднимите версию, запушьте и создайте релиз заново.

### Доверенный издатель отклонил загрузку

Проверьте, что имя окружения GitHub точно совпадает с настроенным в PyPI (с
учётом регистра: `pypi`, `testpypi`). Затем проверьте имя файла workflow — PyPI
ожидает буквально `publish_python.yml`.

### `twine check` падает в CI

Запустите локально, чтобы увидеть точную проблему:

```sh
cd sdk/python
uv sync --locked
uv run python -m build
uv run twine check --strict dist/*
```

Чаще всего: README содержит конструкцию markdown, которую PyPI не может
отрисовать (редко с GitHub-flavored markdown), или удалён/переименован
классификатор.

## Что входит в wheel

Конвейер сборки (см. [.github/workflows/python_test.yml](../../.github/workflows/python_test.yml))
перегенерирует protobuf-код из корневого каталога `proto/` и проверяет, что и
wheel, и sdist содержат:

- `finam_trade_api/` — рукописные модули + реэкспорты по сервисам;
- `finam_trade_api/proto/` — сгенерированные gRPC-заглушки (`.py` + `.pyi`);
- `finam_trade_api/py.typed` — маркер типизации;
- `LICENSE`.

Что *не* входит: `tests/`, `scripts/`, `.venv/`, `__pycache__/`.
