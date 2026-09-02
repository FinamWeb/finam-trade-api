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

Workflow аутентифицируется в npm одним секретом GitHub Actions: `NPM_TOKEN`.

1. На npmjs.com откройте **Access Tokens** и создайте гранулярный токен.
2. Включите **Bypass two-factor authentication**, чтобы GitHub Actions мог
   публиковать без интерактивного ввода.
3. В **Packages and scopes** выдайте доступ **Read and write** к скоупу
   `@finam`. Права на уровне организации сами по себе не дают права публиковать
   пакеты.
4. Дайте токену понятное имя, например `finam-trade-api-github-publish`, и
   выберите подходящий срок действия.
5. В репозитории GitHub откройте **Settings → Secrets and variables →
   Actions**, создайте секрет репозитория с именем `NPM_TOKEN` и вставьте
   токен.

Пользователь npm, создающий токен, должен иметь право публиковать пакеты в
скоупе `@finam`. Ротируйте токен до истечения срока, заменяя тот же секрет
GitHub. Никогда не кладите токен в `.npmrc`, исходный код, YAML workflow, задачи
или логи.

## Создание релиза

1. Выберите одну новую версию, которая ещё не публиковалась ни в одном реестре.
   Обновите версию Python в `sdk/python/pyproject.toml`, JS-привязок в
   `js/package.json` (вместе с `js/package-lock.json`), Kotlin в
   `kotlin/gradle.properties`, затем оба файла Node-пакета:

   ```sh
   cd sdk/node
   npm version 2.19.1 --no-git-tag-version
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
   `2.19.1`. Его публикация запускает все workflow реестров.

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
