'use strict';

/** @type {import('stylelint').Config} */
export default {

    // This Stylelint configuration extends multiple other shared configurations
    extends: [

        // The standard shared configuration for SCSS, which itself extends the standard shared configuration for CSS and the recommended shared
        // configuration for SCSS, the standard shared configuration for CSS also extends the recommended shared configuration for CSS, which means
        // that this configuration pretty much covers all important rules for Stylelint, furthermore, the recommended shared configuration for SCSS
        // also bundles the PostCSS SCSS syntax plugin, which enables Stylelint to parse SCSS, as well as the Stylelint SCSS plugin pack, which
        // contains a collection of SCSS-specific linting rules for Stylelint
        'stylelint-config-standard-scss',

        // The Recess Property Order shared configuration, which sorts CSS properties the way Recess did (a CSS code quality tool from Twitter, which
        // is no longer maintained) and Twitter Bootstrap does (they switched from Recess to Stylelint)
        'stylelint-config-recess-order'
    ],

    // We allow the usage of "stylelint-disable" comments, but they must contain a description in the format "stylelint-disable -- <description>"
    // (enforced by the "reportDescriptionlessDisables" setting), they must match rules that are specified in the configuration (enforced by the
    // "reportInvalidScopeDisables" setting), and they must match lints that need to be disabled (enforced by the "reportNeedlessDisables" setting)
    reportDescriptionlessDisables: true,
    reportInvalidScopeDisables: true,
    reportNeedlessDisables: true,

    // Overrides some of the settings of the standard CSS and SCSS rules to match the coding style followed by the project
    rules: {

        // Although, "!important" should be avoided, there are some cases where it is not possible
        'declaration-no-important': null,

        // Hex color definitions can be shortened, e.g., #55AAFF can be shortened to #5AF; in this project, hex colors should, however, always be
        // defined with the full length, i.e., #55AAFF
        'color-hex-length': 'long',

        // In our SCSS code, we only want to use double-dash comments, i.e., "/* */"-style comments are not allowed
        'scss/comment-no-loud': true,

        // By default, the SCSS standard configuration requires an empty line before comments, except when they are the first non-empty line in a
        // block, we however always require an empty line before a comment, even if the comment is the first non-empty line in a block (since the
        // usage of "/* */"-style comments is not allowed, the "comment-empty-line-before" rule does not need to be configured)
        'scss/double-slash-comment-empty-line-before': [
            'always',
            {
				ignore: ['between-comments', 'stylelint-commands'],
			}
        ]
    }
};
