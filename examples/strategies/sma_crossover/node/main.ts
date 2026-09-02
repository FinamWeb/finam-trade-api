import { pathToFileURL } from "node:url";

import { withTradeApi } from "@finam/trade-api";

import { parseConfig, USAGE } from "./config.js";
import { log, run } from "./runner.js";

const main = async (): Promise<void> => {
  if (process.argv.includes("--help")) {
    console.log(USAGE);
    return;
  }

  const config = parseConfig(process.argv.slice(2));
  if (!config.execute && !config.check) {
    log(config, "WARNING", "Dry-run mode: signals are logged but orders are disabled");
  }
  await withTradeApi({ secret: config.secret }, (api) => run(api, config));
};

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error: unknown) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  });
}
