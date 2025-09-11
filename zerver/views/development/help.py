import os

import werkzeug
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def help_dev_mode_view(request: HttpRequest, subpath: str = "") -> HttpResponse:
    """
    Dev only view that displays help information for setting up the
    help center dev server in the default `run-dev` mode where the
    help center server is not running. Also serves raw MDX content when
    `raw` query param is passed is passed.
    """
    mdx_file_exists = False
    if subpath:
        subpath = werkzeug.utils.secure_filename(subpath)
        mdx_path = os.path.join(
            settings.DEPLOY_ROOT, "starlight_help", "src", "content", "docs", f"{subpath}.mdx"
        )
        mdx_file_exists = os.path.exists(mdx_path) and "/include/" not in mdx_path

        if mdx_file_exists and request.GET.get("raw") == "":
            try:
                with open(mdx_path, encoding="utf-8") as f:
                    content = f.read()
                return HttpResponse(content, content_type="text/plain")
            except OSError:
                return HttpResponse("Error reading MDX file", status=500)

    return render(
        request,
        "zerver/development/dev_help.html",
        {
            "subpath": subpath,
            "mdx_file_exists": mdx_file_exists,
        },
    )
