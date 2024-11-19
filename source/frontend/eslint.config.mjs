
import typeScriptEsLint from 'typescript-eslint';
import virelayEsLintConfig from '@virelay/eslint-config';

// Exports a list of configuration objects that are merged together to create the final configuration object (the typeScriptEsLint.config function is
// used, because it enables us to statically type the configuration objects)
export default typeScriptEsLint.config(

    // Ignores the "node_modules" and ".angular" directories, because they are not part of the project and should not be linted; the "ignores" option
    // must be in its own configuration object, because when it is included in a configuration object with other options, then it only means that the
    // configuration does not apply to the files in the "ignores" option; if it is in its own configuration object, then it means that the specified
    // glob patterns are ignored entirely
    {
        ignores: ['node_modules/*', '.angular/']
    },

    // This is a custom configuration object that adapts the base configuration for the frontend
    {
        // The name of the configuration, which appears in the output of the ESLint CLI
        name: 'ViRelAy ESLint Configuration',

        // Extends the base configuration for ViRelAy
        extends: virelayEsLintConfig,

        // The files that should be linted by ESLint
        files: ['**/*.ts', '**/*.mjs'],

        // Settings related to how JavaScript is configured for linting; here the, we tell the parse to use TypeScript to provide type information for
        // the linting process; the "tsconfigRootDir" tells the parser the absolute path to the directory that contains the tsconfig.json file; all
        // other paths are relative to this directory; the "projectService.defaultProject" option tells the parser to use the tsconfig.eslint.json
        // file, instead of the default tsconfig.json file; this is necessary, because Angular forces us to only reference the app/main.ts file but
        // ESLint requires us to specify all files that are part of the project and should be linted; finally, the "allowDefaultProject" option tells
        // the parser to use the tsconfig.eslint.json file as the project file for the configuration file "config/configuration.production.ts"; this
        // is necessary, because the production configuration file is not referenced by any other file in the project, and therefore does not belong
        // to the project and would not be linted
        languageOptions: {

            // Tells the parser to use TypeScript to provide type information for the linting process; the "projectService" option causes the parser
            // to ask TypeScript's type checking service for type information (some of the files are not included in the TypeScript project; normally,
            // a "tsconfig.eslint.json" file that includes all files should be created and specified it in the "projectService.defaultProject" option;
            // for some reason I cannot get the ESLint-specific TypeScript project to work; the base TypeScript project file "tsconfig.config" only
            // includes the "app/main.ts" file, which means that only the files that reachable from the "app/main.ts" file are included in the
            // project; the "allowedDefaultProject" option allows us to specify additional files that should be included in the project); the
            // "tsconfigRootDir" option tells the parser the absolute path to the "tsconfig.json" TypeScript project file
            parserOptions: {
                tsconfigRootDir: import.meta.dirname,
                projectService: {
                    allowDefaultProject: [
                        'eslint.config.mjs',
                        '.stylelintrc.mjs',
                        'config/configuration.production.ts'
                    ]
                }
            }
        }
    }
);
