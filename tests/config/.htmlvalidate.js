'use strict';

module.exports = {

    // This is the root configuration and HTML-validate should not search for other configuration files
    root: true,

    // For proper validation some metadata for each element is required, detailing in which context it can be used, allowed/disallowed attributes,
    // etc., here the rules permitted by HTML5 are used
    elements: [
        "html5"
    ],

    // A list of configuration presets, on which this configuration is based, here the recommended preset is used, which contains all rules except for
    // some special rules that can be configured to match the code style of the project (e.g., there is a rule, which can be used to validate that all
    // custom HTML attributes adhere to a certain regular expression)
    extends: [
        "html-validate:recommended"
    ],

    // A dictionary of custom rule configuration that are required due to the special circumstances of the project being written in Angular
    rules: {

        // Requires a specific case for attribute names, by default, this would require all attributes to be lower-case, but Angular uses camel-case
        // attributes, so the list of accepted case-styles for HTML attributes must be extended ("ignoreForeign" causes HTML-validate to ignore the
        // casing of attributes on foreign elements, such as <svg> and <math>, as they follow their own specifications, for instance, the SVG
        // specifications uses camel-case for many attributes
        "attr-case": [
            "error",
            {
                "style": ["lowercase", "camelcase"],
                "ignoreForeign": true
            }
        ],

        // HTML void elements are elements which cannot have content and are implicitly closed (<img>); they may, however, optionally be self-closed
        // like XML-style self-closed tags (<img/>); in this project, self-closing void elements are used
        "void-style": [
            "error",
            {
                "style": "selfclosing"
            }
        ],

        // Disallows style tags that contain inline CSS styles
        "no-style-tag": "error",

        // Requires CSS class names to be in kebab-case
        "class-pattern": [
            "error",
            {
                "pattern": "bem"
            }
        ],

        // Requires HTML IDs to be in kebab-case
        "id-pattern": [
            "error",
            {
                "pattern": "kebabcase"
            }
        ],

        // Requires all elements referenced by attributes such as "for" to exist in the current document
        "no-missing-references": "error"
    }
};