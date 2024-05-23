import time
from typing import Any, Dict, List, Optional

import markdown
import markdown.extensions.admonition
import markdown.extensions.codehilite
import markdown.extensions.extra
import markdown.extensions.toc
import orjson
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template import Library, engines
from django.template.backends.jinja2 import Jinja2
from django.utils.safestring import mark_safe

import zerver.lib.markdown.api_arguments_table_generator
import zerver.lib.markdown.api_return_values_table_generator
import zerver.lib.markdown.fenced_code
import zerver.lib.markdown.help_emoticon_translations_table
import zerver.lib.markdown.help_relative_links
import zerver.lib.markdown.help_settings_links
import zerver.lib.markdown.include
import zerver.lib.markdown.include_preprocessor
import zerver.lib.markdown.nested_code_blocks
import zerver.lib.markdown.static
import zerver.lib.markdown.tabbed_sections
import zerver.openapi.markdown_extension
from zerver.lib.cache import dict_to_items_tuple, ignore_unhashable_lru_cache, items_tuple_to_dict

register = Library()


def and_n_others(values: List[str], limit: int) -> str:
    # A helper for the commonly appended "and N other(s)" string, with
    # the appropriate pluralization.
    return " and {} other{}".format(
        len(values) - limit,
        "" if len(values) == limit + 1 else "s",
    )


@register.filter(name="display_list", is_safe=True)
def display_list(values: List[str], display_limit: int) -> str:
    """
    Given a list of values, return a string nicely formatting those values,
    summarizing when you have more than `display_limit`. Eg, for a
    `display_limit` of 3 we get the following possible cases:

    Jessica
    Jessica and Waseem
    Jessica, Waseem, and Tim
    Jessica, Waseem, Tim, and 1 other
    Jessica, Waseem, Tim, and 2 others
    """
    if len(values) == 1:
        # One value, show it.
        display_string = f"{values[0]}"
    elif len(values) <= display_limit:
        # Fewer than `display_limit` values, show all of them.
        display_string = ", ".join(f"{value}" for value in values[:-1])
        display_string += f" and {values[-1]}"
    else:
        # More than `display_limit` values, only mention a few.
        display_string = ", ".join(f"{value}" for value in values[:display_limit])
        display_string += and_n_others(values, display_limit)

    return display_string


md_extensions: Optional[List[markdown.Extension]] = None
md_macro_extension: Optional[markdown.Extension] = None
# Prevent the automatic substitution of macros in these docs. If
# they contain a macro, it is always used literally for documenting
# the macro system.
docs_without_macros = [
    "incoming-webhooks-walkthrough.md",
]

def convert_to_mdx(self, source: str) -> str:
        """
        Convert a Markdown string to a string in the specified output format.

        Arguments:
            source: Markdown formatted text as Unicode or ASCII string.

        Returns:
            A string in the specified output format.

        Markdown parsing takes place in five steps:

        1. A bunch of [`preprocessors`][markdown.preprocessors] munge the input text.
        2. A [`BlockParser`][markdown.blockparser.BlockParser] parses the high-level structural elements of the
           pre-processed text into an [`ElementTree`][xml.etree.ElementTree.ElementTree] object.
        3. A bunch of [`treeprocessors`][markdown.treeprocessors] are run against the
           [`ElementTree`][xml.etree.ElementTree.ElementTree] object. One such `treeprocessor`
           ([`markdown.treeprocessors.InlineProcessor`][]) runs [`inlinepatterns`][markdown.inlinepatterns]
           against the [`ElementTree`][xml.etree.ElementTree.ElementTree] object, parsing inline markup.
        4. Some [`postprocessors`][markdown.postprocessors] are run against the text after the
           [`ElementTree`][xml.etree.ElementTree.ElementTree] object has been serialized into text.
        5. The output is returned as a string.

        """

        # Fix up the source text
        if not source.strip():
            return ''  # a blank Unicode string

        try:
            source = str(source)
        except UnicodeDecodeError as e:  # pragma: no cover
            # Customize error message while maintaining original traceback
            e.reason += '. -- Note: Markdown only accepts Unicode input!'
            raise

        # Split into lines and run the line preprocessors.
        self.lines = source.split("\n")
        for prep in self.preprocessors:
            self.lines = prep.run(self.lines)
        
        return "\n".join(self.lines)

    #     # Parse the high-level elements.
    #     root = self.parser.parseDocument(self.lines).getroot()
    #     #MAYBE WE NEED TO CONVERT IN BACK TO MARKDOWN USING MARKDOWNIFY
    #     print(self.parser.parseDocument(self.lines).write('test.xml'))
    #    # return root

        # Run the tree-processors
        # for treeprocessor in self.treeprocessors:
        #     newRoot = treeprocessor.run(root)
        #     if newRoot is not None:
        #         root = newRoot
    
        # return root

        # # Serialize _properly_.  Strip top-level tags.
        output = self.serializer(root)
        # if self.stripTopLevelTags:
        #     try:
        #         start = output.index(
        #             '<%s>' % self.doc_tag) + len(self.doc_tag) + 2
        #         end = output.rindex('</%s>' % self.doc_tag)
        #         output = output[start:end].strip()
        #     except ValueError as e:  # pragma: no cover
        #         if output.strip().endswith('<%s />' % self.doc_tag):
        #             # We have an empty document
        #             output = ''
        #         else:
        #             # We have a serious problem
        #             raise ValueError('Markdown failed to strip top-level '
        #                              'tags. Document=%r' % output.strip()) from e

        # # Run the text post-processors
        # for pp in self.postprocessors:
        #     output = pp.run(output)

        # return output.strip()

markdown.Markdown.convert_to_mdx = convert_to_mdx

# render_markdown_path is passed a context dictionary (unhashable), which
# results in the calls not being cached. To work around this, we convert the
# dict to a tuple of dict items to cache the results.
@dict_to_items_tuple
@ignore_unhashable_lru_cache(512)
@items_tuple_to_dict
@register.filter(name="render_markdown_path", is_safe=True)
def render_markdown_path(
    markdown_file_path: str,
    context: Optional[Dict[str, Any]] = None,
    integration_doc: bool = False,
    help_center: bool = False,
) -> str:
    """Given a path to a Markdown file, return the rendered HTML.

    Note that this assumes that any HTML in the Markdown file is
    trusted; it is intended to be used for documentation, not user
    data."""

    # We set this global hackishly
    from zerver.lib.markdown.help_settings_links import set_relative_settings_links

    set_relative_settings_links(bool(context is not None and context.get("html_settings_links")))
    from zerver.lib.markdown.help_relative_links import set_relative_help_links

    set_relative_help_links(bool(context is not None and context.get("html_settings_links")))

    global md_extensions
    global md_macro_extension
    if md_extensions is None:
        md_extensions = [
            markdown.extensions.extra.makeExtension(),
            markdown.extensions.toc.makeExtension(),
            markdown.extensions.admonition.makeExtension(),
            markdown.extensions.codehilite.makeExtension(
                linenums=False,
                guess_lang=False,
            ),
            zerver.lib.markdown.fenced_code.makeExtension(
                run_content_validators=bool(
                    context is not None and context.get("run_content_validators", False)
                ),
            ),
            zerver.lib.markdown.api_arguments_table_generator.makeExtension(),
            zerver.lib.markdown.api_return_values_table_generator.makeExtension(),
            zerver.lib.markdown.nested_code_blocks.makeExtension(),
            zerver.lib.markdown.tabbed_sections.makeExtension(),
            zerver.lib.markdown.help_settings_links.makeExtension(),
            zerver.lib.markdown.help_relative_links.makeExtension(),
            zerver.lib.markdown.help_emoticon_translations_table.makeExtension(),
            zerver.lib.markdown.static.makeExtension(),
        ]
    if context is not None and "api_url" in context:
        # We need to generate the API code examples extension each
        # time so the `api_url` config parameter can be set dynamically.
        #
        # TODO: Convert this to something more efficient involving
        # passing the API URL as a direct parameter.
        extensions = [
            zerver.openapi.markdown_extension.makeExtension(
                api_url=context["api_url"],
            ),
            *md_extensions,
        ]
    else:
        extensions = md_extensions

    if integration_doc:
        md_macro_extension = zerver.lib.markdown.include.makeExtension(
            base_path="templates/zerver/integrations/include/"
        )
    elif help_center:
        pre_macro_extension = zerver.lib.markdown.include_preprocessor.makeExtension(base_path="help/include/")
        extensions = [pre_macro_extension, *extensions]
        md_macro_extension = zerver.lib.markdown.include.makeExtension(base_path="help/include/")
    else:
        md_macro_extension = zerver.lib.markdown.include.makeExtension(
            base_path="api_docs/include/"
        )
    if not any(doc in markdown_file_path for doc in docs_without_macros):
        extensions = [md_macro_extension, *extensions]

    md_engine = markdown.Markdown(extensions=extensions)
    md_engine.reset()

    jinja = engines["Jinja2"]
    assert isinstance(jinja, Jinja2)
    if markdown_file_path.startswith("/"):
        with open(markdown_file_path) as fp:
            markdown_string = fp.read()
    else:
        markdown_string = jinja.env.loader.get_source(jinja.env, markdown_file_path)[0]

    API_ENDPOINT_NAME = context.get("API_ENDPOINT_NAME", "") if context is not None else ""
    markdown_string = markdown_string.replace("API_ENDPOINT_NAME", API_ENDPOINT_NAME)
    print('yay')
    print(md_engine.convert_to_mdx(markdown_string))
    print('nay')
    html = md_engine.convert(markdown_string)
    if context is None:
        return mark_safe(html)  # noqa: S308

    return mark_safe(jinja.from_string(html).render(context))  # noqa: S308


def webpack_entry(entrypoint: str) -> List[str]:
    while True:
        with open(settings.WEBPACK_STATS_FILE, "rb") as f:
            stats = orjson.loads(f.read())
        status = stats["status"]
        if not settings.DEBUG or status != "compile":
            break
        time.sleep(0.2)

    if status != "done":
        raise RuntimeError("Webpack compilation was not successful")

    try:
        files_from_entrypoints = [
            staticfiles_storage.url(settings.WEBPACK_BUNDLES + filename)
            for filename in stats["chunks"][entrypoint]
            if filename.endswith((".css", ".js")) and not filename.endswith(".hot-update.js")
        ]
    except KeyError:
        raise KeyError(
            f"'{entrypoint}' entrypoint could not be found. Please define it in web/webpack.assets.json."
        )

    return files_from_entrypoints
