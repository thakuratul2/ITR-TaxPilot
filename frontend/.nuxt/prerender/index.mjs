import process from 'node:process';globalThis._importMeta_={url:import.meta.url,env:process.env};import { t as trapUnhandledNodeErrors, u as useNitroApp } from './chunks/_/nitro.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/h3/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/destr/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/hookable/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/ofetch/dist/node.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/node-mock-http/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/ufo/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/unstorage/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/unstorage/drivers/fs.mjs';
import 'file:///D:/Projects/ITR-TaxPilot/frontend/node_modules/@nuxt/nitro-server/dist/runtime/utils/cache-driver.js';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/unstorage/drivers/fs-lite.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/ohash/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/klona/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/defu/dist/defu.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/scule/dist/index.mjs';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/radix3/dist/index.mjs';
import 'node:fs';
import 'node:url';
import 'file://D:/Projects/ITR-TaxPilot/frontend/node_modules/pathe/dist/index.mjs';

const nitroApp = useNitroApp();
const localFetch = nitroApp.localFetch;
const closePrerenderer = () => nitroApp.hooks.callHook("close");
trapUnhandledNodeErrors();

export { closePrerenderer, localFetch };
//# sourceMappingURL=index.mjs.map
