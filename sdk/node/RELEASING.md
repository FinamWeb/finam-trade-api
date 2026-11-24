# Выпуск SDK

Все SDK репозитория используют одну версию и один GitHub Release:

- `finam-sdk` публикуется в PyPI (`.github/workflows/publish_python.yml`);
- `@finam/trade-api` публикуется в npm (`.github/workflows/publish_node.yml`);
- `@finam/grpc-tradeapi` — JS-привязки из `js/` — публикуются в npm
  (`.github/workflows/publish_js_proto.yml`);
- Kotlin SDK публикуется в Maven Central
  (`.github/workflows/publish_sdk_proto.yml`).

Этот документ — общий чеклист. Настройка, специфичная для PyPI, описана в
[руководстве Python SDK](../python/RELEASING.md).

## Разовая настройка npm

Workflow аутентифицируется в npm через trusted publishing (OIDC): GitHub
Actions на каждый запуск получает короткоживущие учётные данные, поэтому npm-токен
в репозитории не хранится и не требует ротации. npm автоматически прикладывает к
пакету provenance-аттестацию.

1. На npmjs.com откройте страницу пакета `@finam/trade-api` → **Settings** →
   **Trusted publishing** и добавьте издателя **GitHub Actions**:
   - Organization or user: `FinamWeb`
   - Repository: `finam-trade-api`
   - Workflow filename: `publish_node.yml`
   - Environment: оставьте пустым.
2. Настраивать издателя может владелец пакета или скоупа `@finam`.
3. Trusted publishing настраивается только для уже существующего пакета. Если
   `@finam/trade-api` ещё не опубликован, выполните первую публикацию вручную с
   учётной записи, имеющей право публиковать в `@finam`, затем добавьте издателя.
4. После первого успешного релиза через OIDC включите в **Settings** пакета
   запрет публикации токенами и отзовите прежний токен, а секрет `NPM_TOKEN`
   удалите из **Settings → Secrets and variables → Actions**.

Никогда не кладите npm-токен в `.npmrc`, исходный код, YAML workflow, задачи
или логи.

## Создание релиза

1. Выберите одну новую версию, которая ещё не публиковалась ни в одном реестре.
   Обновите версию Python в `sdk/python/pyproject.toml`, JS-привязок в
   `js/package.json` (вместе с `js/package-lock.json`), Kotlin в
   `kotlin/gradle.properties`, затем оба файла Node-пакета:

   ```sh
   cd sdk/node
   npm version 2.24.0 --no-git-tag-version
   ```

2. Перегенерируйте и проверьте оба SDK:

   ```sh
   cd ../..
   just bootstrap
   just check

   npm --prefix sdk/node run build
   npm --prefix sdk/node pack --dry-run
   ```

3. Закоммитьте повышение версии. Сгенерированные привязки пересоздаются во
   время сборок CI.
4. Создайте один GitHub Release на этот коммит с «голым» тегом версии, например
   `2.24.0`. Его публикация запускает все workflow реестров.

Стабильные версии публикуются в PyPI и под тегом npm `latest`. Пререлизы
публикуются в TestPyPI и под тегом npm `next`.

Workflow Node можно запустить и вручную с существующим тегом версии. Тег должен
указывать на коммит с совпадающими версиями Python и Node.

5. После первой публикации новой версии обновите примеры-потребители: замените
   зафиксированные версии в `examples/sdk/*/` и `examples/strategies/*/*/`
   на опубликованную, перегенерируйте `uv.lock` (`uv lock`) и
   `package-lock.json` (`npm install --package-lock-only`) и закоммитьте их
   отдельным изменением. Именно так примеры остаются тестом опубликованного
   пакета, а не исходников.

## Что проверяет workflow

До защищённого шага публикации CI:

- сверяет тег релиза с версиями пакетов Python и Node;
- перегенерирует protobuf-код из исходных контрактов на теге;
- проверяет типы SDK, тестов и примеров;
- прогоняет внутрипроцессный интеграционный набор gRPC;
- собирает и упаковывает пакет;
- устанавливает tarball в пустой проект-потребитель и импортирует его публичные
  точки входа.

Публикуется ровно тот tarball, который прошёл эти проверки.
