module.exports = {
  root: true,
  env: { browser: true, es2021: true },
  parserOptions: { ecmaVersion: "latest", sourceType: "module" },
  plugins: ["react", "react-hooks"],
  extends: ["eslint:recommended", "plugin:react/recommended"],
  settings: { react: { version: "detect" } },
  rules: {
    "react/react-in-jsx-scope": "off"
  }
};
