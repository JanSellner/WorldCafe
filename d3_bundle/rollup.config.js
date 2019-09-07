import node from "rollup-plugin-node-resolve";

export default {
  input: "index.js",
  output: {
    format: "umd",
    file: "d3.js"
  },
  name: "d3",
  plugins: [node()],
  sourcemap: false
};