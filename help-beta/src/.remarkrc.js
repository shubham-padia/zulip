// The starting set of rules for this file were borrowed from
// https://github.com/wooorm/remark-preset-wooorm, some of the rules
// that we did not want were removed from the starting set. None of the
// rules were giving an error on the starting set, but some rules that
// were giving lots of warnings on the generated mdx were removed, we
// can add them back later as and when required.

import remarkCommentConfig from "remark-comment-config";
import remarkFrontmatter from "remark-frontmatter";
import remarkLintBlockquoteIndentation from "remark-lint-blockquote-indentation";
import remarkLintCheckboxCharacterStyle from "remark-lint-checkbox-character-style";
import remarkLintCheckboxContentIndent from "remark-lint-checkbox-content-indent";
import remarkLintCodeBlockStyle from "remark-lint-code-block-style";
import remarkLintCorrectMediaSyntax from "remark-lint-correct-media-syntax";
import remarkLintEmphasisMarker from "remark-lint-emphasis-marker";
import remarkLintFencedCodeMarker from "remark-lint-fenced-code-marker";
import remarkLintFileExtension from "remark-lint-file-extension";
import remarkLintHardBreakSpaces from "remark-lint-hard-break-spaces";
import remarkLintHeadingStyle from "remark-lint-heading-style";
import remarkLintLinkTitleStyle from "remark-lint-link-title-style";
import remarkLintMdxJsxNoVoidChildren from "remark-lint-mdx-jsx-no-void-children";
import remarkLintMdxJsxQuoteStyle from "remark-lint-mdx-jsx-quote-style";
import remarkLintMdxJsxSelfClose from "remark-lint-mdx-jsx-self-close";
import remarkLintMdxJsxShorthandAttribute from "remark-lint-mdx-jsx-shorthand-attribute";
import remarkLintMdxJsxUniqueAttributeName from "remark-lint-mdx-jsx-unique-attribute-name";
import remarkLintNoDuplicateHeadingsInSection from "remark-lint-no-duplicate-headings-in-section";
import remarkLintNoEmphasisAsHeading from "remark-lint-no-emphasis-as-heading";
import remarkLintNoEmptyUrl from "remark-lint-no-empty-url";
import remarkLintNoHeadingContentIndent from "remark-lint-no-heading-content-indent";
import remarkLintNoHeadingIndent from "remark-lint-no-heading-indent";
import remarkLintNoHeadingLikeParagraph from "remark-lint-no-heading-like-paragraph";
import remarkLintNoHiddenTableCell from "remark-lint-no-hidden-table-cell";
import remarkLintNoHtml from "remark-lint-no-html";
import remarkLintNoMultipleToplevelHeadings from "remark-lint-no-multiple-toplevel-headings";
import remarkLintNoParagraphContentIndent from "remark-lint-no-paragraph-content-indent";
import remarkLintNoReferenceLikeUrl from "remark-lint-no-reference-like-url";
import remarkLintNoShellDollars from "remark-lint-no-shell-dollars";
import remarkLintNoTableIndentation from "remark-lint-no-table-indentation";
import remarkLintNoTabs from "remark-lint-no-tabs";
import remarkLintNoUnneededFullReferenceImage from "remark-lint-no-unneeded-full-reference-image";
import remarkLintNoUnneededFullReferenceLink from "remark-lint-no-unneeded-full-reference-link";
import remarkLintNoUnusedDefinitions from "remark-lint-no-unused-definitions";
import remarkLintRuleStyle from "remark-lint-rule-style";
import remarkLintStrongMarker from "remark-lint-strong-marker";
import remarkLintTableCellPadding from "remark-lint-table-cell-padding";
import remarkLintTablePipeAlignment from "remark-lint-table-pipe-alignment";
import remarkLintTablePipes from "remark-lint-table-pipes";
import remarkLintUnorderedListMarkerStyle from "remark-lint-unordered-list-marker-style";
import remarkLintRulesLintRecommended from "remark-preset-lint-recommended";
import stringWidth from "string-width";

const remarkLintRules = {
    plugins: [
        remarkLintRulesLintRecommended,
        remarkCommentConfig,
        [remarkLintBlockquoteIndentation, 2],
        [remarkLintCheckboxCharacterStyle, {checked: "x", unchecked: " "}],
        remarkLintCheckboxContentIndent,
        [remarkLintCodeBlockStyle, "fenced"],
        remarkLintCorrectMediaSyntax,
        [remarkLintEmphasisMarker, "*"],
        [remarkLintFencedCodeMarker, "`"],
        [remarkLintFileExtension, ["mdx"]],
        [remarkLintHardBreakSpaces, {allowSpaces: false}],
        [remarkLintHeadingStyle, "atx"],
        [remarkLintLinkTitleStyle, '"'],
        remarkLintMdxJsxNoVoidChildren,
        [remarkLintMdxJsxQuoteStyle, '"'],
        remarkLintMdxJsxSelfClose,
        remarkLintMdxJsxShorthandAttribute,
        remarkLintMdxJsxUniqueAttributeName,
        remarkLintNoDuplicateHeadingsInSection,
        remarkLintNoEmphasisAsHeading,
        remarkLintNoEmptyUrl,
        remarkLintNoHeadingContentIndent,
        remarkLintNoHeadingIndent,
        remarkLintNoHeadingLikeParagraph,
        remarkLintNoHiddenTableCell,
        remarkLintNoHtml,
        remarkLintNoMultipleToplevelHeadings,
        remarkLintNoParagraphContentIndent,
        remarkLintNoReferenceLikeUrl,
        remarkLintNoShellDollars,
        remarkLintNoTableIndentation,
        remarkLintNoTabs,
        remarkLintNoUnneededFullReferenceImage,
        remarkLintNoUnneededFullReferenceLink,
        [remarkLintRuleStyle, "***"],
        [remarkLintStrongMarker, "*"],
        [remarkLintTableCellPadding, {stringLength: stringWidth, style: "padded"}],
        [remarkLintTablePipeAlignment, {stringLength: stringWidth}],
        remarkLintTablePipes,
        [remarkLintUnorderedListMarkerStyle, "*"],
        [remarkLintNoUnusedDefinitions, false],
    ],
};

const config = {
    plugins: [[remarkFrontmatter, ["yaml"]], remarkLintRules],
};

export default config;
