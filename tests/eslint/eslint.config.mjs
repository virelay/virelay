
import globals from 'globals';
import javaScriptEsLint from '@eslint/js';
import typeScriptEsLint from 'typescript-eslint';
import angularEsLint from 'angular-eslint';

// Exports a list of configuration objects that are merged together to create the final configuration object (the typeScriptEsLint.config function is
// used, because it enables us to statically type the configuration objects)
export default typeScriptEsLint.config(

    // Extends the recommended configuration from the ESLint core rules
    javaScriptEsLint.configs.recommended,

    // Extends the strict-type-checked configuration from the TypeScript ESLint plugin, which contains the recommended rules, additional recommended
    // rules that require type information, and additional strict rules that can also catch bugs
    ...typeScriptEsLint.configs.strictTypeChecked,

    // Extends the stylistic-type-checked configuration from the TypeScript ESLint plugin, which contains the stylistic rules that are considered to
    // be best practice for modern TypeScript code bases, but that do not impact program logic, as well as additional stylistic rules that require
    // type information
    ...typeScriptEsLint.configs.stylisticTypeChecked,

    // Extends the recommended configuration from the Angular ESLint plugin, which contains the recommended rules for Angular applications
    ...angularEsLint.configs.tsRecommended,

    // This is a custom configuration object that customizes the rules of the extended shared configurations above
    {
        // The name of the configuration, which appears in the output of the ESLint CLI
        name: 'ViRelAy ESLint Base Configuration',

        // Settings related to how JavaScript is configured for linting; here the; global variables that are available in the browser environment are
        // added to the global scope during linting
        languageOptions: {
            globals: globals.browser
        },

        // Customizes the rules of the extended shared configurations above
        rules: {

            // This rule enforces that explicit types of variables that can be trivially inferred from the initialization should be removed; in this
            // project we want to be consistent and always specify the type, even if it can be inferred from the value it is initialized with
            '@typescript-eslint/no-inferrable-types': 'off',

            // This rule enforces that no classes that only have static members or have no members at all must be declared; this rule is turned off,
            // because it incorrectly identifies classes that have public non-static properties as extraneous (maybe this is because of the
            // "accessor" syntax in TypeScript, which auto-implements getters and setters for properties)
            '@typescript-eslint/no-extraneous-class': 'off',

            // This rule enforces that only strings are allowed to be used in string template expressions; we, however, also allow numbers and
            // booleans to be used in string template expressions, because they are automatically converted to strings; they are often used and the
            // chances of them being used incorrectly are low
            '@typescript-eslint/restrict-template-expressions': [
                'error',
                {
                    allowNumber: true,
                    allowBoolean: true
                }
            ]
        }
    }
);
