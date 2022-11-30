module.exports = {
  globals: {
    __PATH_PREFIX__: true,
    __DEV__: false,
    __TEST__: false,
    __PROD__: false,
    __DEBUG__: false,
    __COVERAGE__: false,
    __BASENAME__: false,
  },
  parser: "babel-eslint",
  extends: ["react-app"],
  plugins: ["babel", "react", "react-hooks"],
  env: {
    browser: true,
    es6: true,
  },
  parserOptions: {
    ecmaVersion: 2016,
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    "arrow-parens": 0,
    "no-undef": 0,
    "import/no-named-as-default": 0,
    "no-param-reassign": 0,
    "no-unused-expressions": 0,
    "import/no-extraneous-dependencies": 0,
    "import/no-unresolved": 0,
    "import/extensions": 0,
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "react/jsx-filename-extension": [1, { extensions: [".js", ".jsx"] }],
    "react/jsx-closing-bracket-location": 0,
    "no-shadow": 0,
    "react/no-danger": 0,
    "react/jsx-props-no-spreading": 0,
    "import/prefer-default-export": 0,
    "import/no-webpack-loader-syntax": 0,
    "react/jsx-space-before-closing": 0,
    "jsx-a11y/href-no-hash": "off",
    "jsx-a11y/anchor-is-valid": "off",
    "no-console": "off",
    "linebreak-style": "off",
    "no-underscore-dangle": ["error", { allow: ["_id"] }],
  },
};
