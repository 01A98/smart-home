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

const tsFiles = fs
  .readdirSync("templates/pages")
  .filter((file) => file.endsWith(".ts"));

const configs = tsFiles.map((file) => ({
  input: "templates/pages/" + file,
  output: {
    sourcemap: true,
    format: "iife",
    dir: "public/pages",
    entryFileNames: "[name].[hash].js",
    // etc
  },
  plugins: [
    {
      name: "cleanOutputDir",
      buildStart() {
        const DIR_PATH = "public/pages";
        let files;
        try {
          files = fs.readdirSync(DIR_PATH);
        } catch (err) {
          switch (err.code) {
            case "ENOENT":
              return; // Noop when directory don't exists.
            case "ENOTDIR":
              throw new Error(`'${DIR_PATH}' is not a directory.`);
            default:
              throw err;
          }
        }
        for (const file of files) {
          const filePath = path.join(DIR_PATH, file);
          fs.rmSync(filePath, { recursive: true });
        }
      },
    },
    peerDepsExternal(),
    resolve(),
    commonjs(),
    typescript({
      // useTsconfigDeclarationDir: true,
      // tsconfigOverride: {
      //   exclude: ["**/*.stories.*"],
      // },
    }),
    commonjs({
      exclude: "node_modules",
      ignoreGlobal: true,
    }),
    // // even livereload can work if you specify a different port for each entry point
    // livereload({
    //   watch: `public/${name}.*`,
    //   port: 3000 + index,
    // }),
  ],
  external: Object.keys(externalDeps),
}));

module.exports = configs;
