from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.http import register_exception_handlers, register_http_middleware


def _landing_html(*, base_url: str, app_name: str, app_version: str, api_version: str) -> str:
    """Build the root landing page HTML."""
    docs_url = f"{base_url}/docs"
    openapi_url = f"{base_url}/openapi.json"
    api_url = f"{base_url}/api"
    title = f"{app_name} - Indonesia Administrative Region API"
    description = (
        "Production-ready FastAPI service for Indonesian administrative region data "
        "across province, regency/city, district, and village levels."
    )
    keywords = (
        "wilayah indonesia api, fastapi indonesia, provinsi kabupaten kecamatan desa, "
        "kode wilayah indonesia"
    )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <meta name="description" content="{description}" />
    <meta name="keywords" content="{keywords}" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{base_url}/" />
    <link rel="icon" href="https://rone.dev/static/img/favicon/favicon.ico" />

    <meta property="og:type" content="website" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{base_url}/" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />

    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script type="application/ld+json">
      {{
        "@context": "https://schema.org",
        "@type": "WebAPI",
        "name": "{app_name}",
        "description": "{description}",
        "url": "{api_url}",
        "documentation": "{docs_url}",
        "version": "{app_version}"
      }}
    </script>
  </head>
  <body class="min-h-screen bg-black text-zinc-100 antialiased">
    <main class="mx-auto w-full max-w-6xl px-6 py-12 sm:px-8 lg:py-16">
      <header class="border border-zinc-800 bg-transparent p-8">
        <p class="text-xs uppercase tracking-[0.2em] text-zinc-400">{api_version}</p>
        <h1 class="mt-3 text-3xl font-semibold sm:text-5xl">{app_name}</h1>
        <p class="mt-4 max-w-3xl text-sm leading-relaxed text-zinc-300 sm:text-base">
          Fast and consistent API for Indonesia administrative regions with standardized
          envelopes, recursive parent chains, and complete level coverage.
        </p>
      </header>

      <section class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <a href="{api_url}" class="border border-zinc-800 bg-transparent p-5 transition hover:border-zinc-500">
          <h2 class="text-lg font-medium">API Root</h2>
          <p class="mt-2 text-sm text-zinc-400">Explore route groups and base metadata.</p>
        </a>
        <a href="{docs_url}" class="border border-zinc-800 bg-transparent p-5 transition hover:border-zinc-500">
          <h2 class="text-lg font-medium">Swagger Docs</h2>
          <p class="mt-2 text-sm text-zinc-400">Interactive endpoint testing and schemas.</p>
        </a>
        <a href="{openapi_url}" class="border border-zinc-800 bg-transparent p-5 transition hover:border-zinc-500">
          <h2 class="text-lg font-medium">OpenAPI JSON</h2>
          <p class="mt-2 text-sm text-zinc-400">Machine-readable API contract.</p>
        </a>
      </section>

      <section class="mt-8 border border-zinc-800 bg-transparent p-6">
        <h2 class="text-xl font-medium">Available Namespaces</h2>
        <div class="mt-4 grid gap-3 text-sm text-zinc-300 sm:grid-cols-2">
          <p><span class="text-zinc-500">Root:</span> /api</p>
          <p><span class="text-zinc-500">Search:</span> /api/kode/{{kode}}</p>
          <p><span class="text-zinc-500">Hierarchy:</span> /api/0, /api/{{prov}}/...</p>
          <p><span class="text-zinc-500">Simple:</span> /api/s/{{prov}}/{{kab}}/{{kec}}/{{desa}}</p>
        </div>
      </section>
    </main>
  </body>
</html>
"""


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API data wilayah administratif Indonesia untuk level provinsi, "
            "kabupaten/kota, kecamatan, dan desa/kelurahan."
        ),
        redirect_slashes=True,
        openapi_tags=[
            {"name": "root", "description": "Informasi dasar API pada namespace /api."},
            {"name": "search", "description": "Pencarian wilayah berdasarkan kode penuh pada /api/kode/{kode}."},
            {
                "name": "wilayah",
                "description": "Endpoint hierarki kode penuh pada namespace /api.",
            },
            {
                "name": "simple",
                "description": (
                    "Endpoint shorthand pada /api/s. "
                    "Tingkat 1 = provinsi, tingkat 2 = kabupaten/kota, "
                    "tingkat 3 = kecamatan, tingkat 4 = desa/kelurahan."
                ),
            },
        ],
    )

    if settings.allowed_origins_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins_list,
            allow_methods=["GET"],
            allow_headers=["Accept", "Accept-Language", "Content-Type"],
            max_age=86400,
        )

    register_http_middleware(app)
    register_exception_handlers(app)

    @app.get("/", include_in_schema=False, response_class=HTMLResponse)
    async def landing_page(request: Request) -> HTMLResponse:
        """Serve the public landing page at the root URL."""
        base_url = str(request.base_url).rstrip("/")
        return HTMLResponse(
            _landing_html(
                base_url=base_url,
                app_name=settings.app_name,
                app_version=settings.app_version,
                api_version=settings.api_version,
            )
        )

    app.include_router(api_router)
    return app


app = create_app()
