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
const TEMPLATE_VIEWS_DIR = path.join(TEMPLATE_ROOT_DIR, "views");
const TEMPLATE_MACROS_DIR = path.join(TEMPLATE_ROOT_DIR, "macros");

const tsFileInRoot = fs
  .readdirSync(TEMPLATE_ROOT_DIR)
  .filter((file) => file.endsWith(".ts"))
  .map((file) => ({ file, inputDir: TEMPLATE_ROOT_DIR }));

const tsFilesInViews = fs
  .readdirSync(TEMPLATE_VIEWS_DIR, { withFileTypes: true })
  .filter((dirent) => dirent.isDirectory())
  .flatMap((dirent) =>
    fs
      .readdirSync(path.join(dirent.path, dirent.name))
      .filter((file) => file.endsWith(".ts"))
      .map((file) => ({
        file,
        inputDir: path.join(TEMPLATE_VIEWS_DIR, dirent.name),
      }))
  );

const tsFilesInComponents = fs
  .readdirSync(TEMPLATE_MACROS_DIR)
  .filter((file) => file.endsWith(".ts"))
  .map((file) => ({ file, inputDir: TEMPLATE_MACROS_DIR }));

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
  ...tsFileInRoot.map(({ file, inputDir }) => getConfig(file, inputDir)),
  ...tsFilesInViews.map(({ file, inputDir }) => getConfig(file, inputDir)),
  ...tsFilesInComponents.map(({ file, inputDir }) => getConfig(file, inputDir)),
];

module.exports = configs;
