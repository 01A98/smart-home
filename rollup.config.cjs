const peerDepsExternal = require("rollup-plugin-peer-deps-external");
const resolve = require("@rollup/plugin-node-resolve");
const commonjs = require("@rollup/plugin-commonjs");
const typescript = require("rollup-plugin-typescript2");
const fs = require("fs");
const path = require("path");

// this override is needed because Module format cjs does not support top-level await
// eslint-disable-next-line @typescript-eslint/no-var-requires
const packageJson = require("./package.json");

const externalDeps = {
  ...packageJson.devDependencies,
};

const TEMPLATE_ROOT_DIR = "templates";
const TEMPLATE_PAGES_DIR = path.join(TEMPLATE_ROOT_DIR, "pages");
const TEMPLATE_COMPONENTS_DIR = path.join(TEMPLATE_ROOT_DIR, "components");

const tsFileInRoot = fs
  .readdirSync(TEMPLATE_ROOT_DIR)
  .filter((file) => file.endsWith(".ts"));

const tsFilesInPages = fs
  .readdirSync(TEMPLATE_PAGES_DIR)
  .filter((file) => file.endsWith(".ts"));

const tsFilesInComponents = fs
  .readdirSync(TEMPLATE_COMPONENTS_DIR)
  .filter((file) => file.endsWith(".ts"));

const getConfig = (file, inputDir) => {
  const outputDir = inputDir.replace("templates", "public");
  return {
    input: path.join(inputDir, file),
    output: {
      sourcemap: true,
      dir: outputDir,
      entryFileNames: "[name].[hash].js",
    },
    plugins: [
      {
        name: "cleanOutputDir",
        buildStart() {
          const DIR_PATH = outputDir;
          let dir;
          try {
            dir = fs.readdirSync(DIR_PATH);
          } catch (err) {
            switch (err.code) {
              case "ENOENT":
                return;
              case "ENOTDIR":
                throw new Error(`'${DIR_PATH}' is not a directory.`);
              default:
                throw err;
            }
          }
          for (const filename of dir) {
            const filePath = path.join(DIR_PATH, filename);
            const filenameNoExtensions = filename.split(".")[0];
            if (filenameNoExtensions === path.parse(file).name) {
              fs.rmSync(filePath, { recursive: true });
            }
          }
        },
      },
      peerDepsExternal(),
      resolve(),
      commonjs(),
      typescript({}),
      commonjs({
        exclude: "node_modules",
        ignoreGlobal: true,
      }),
    ],
    external: Object.keys(externalDeps),
  };
};

const configs = [
  ...tsFileInRoot.map((file) => getConfig(file, TEMPLATE_ROOT_DIR)),
  ...tsFilesInPages.map((file) => getConfig(file, TEMPLATE_PAGES_DIR)),
  ...tsFilesInComponents.map((file) =>
    getConfig(file, TEMPLATE_COMPONENTS_DIR)
  ),
];

module.exports = configs;
