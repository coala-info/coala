# Tool Agent Documentation

This directory contains the documentation website for Tool Agent, built with [VitePress](https://vitepress.dev/).

## Local Development

### Prerequisites

- Node.js 18+ and npm

### Setup

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

The site will be available at `http://localhost:5173`

### Build

To build the site for production:

```bash
npm run build
```

The built files will be in `.vitepress/dist/`

### Preview Production Build

To preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
docs/
├── .vitepress/          # VitePress configuration
│   ├── config.mts       # Main configuration file
│   └── theme/           # Custom theme overrides
├── guide/               # Guide documentation
│   ├── index.md
│   ├── installation.md
│   ├── quick-start.md
│   ├── mcp-server.md
│   └── function-call.md
├── use-cases/           # Use case examples
│   └── tp53-gene-analysis.md
├── index.md            # Homepage
└── package.json        # Dependencies and scripts
```

## Adding New Documentation

Simply add new markdown files to the appropriate directory:

- **Guide pages**: Add to `guide/` directory
- **Use cases**: Add to `use-cases/` directory
- **Other pages**: Add to root or create new directories

Then update the sidebar configuration in `.vitepress/config.mts` to include the new pages.

## GitHub Pages Deployment

The repository includes a GitHub Actions workflow (`.github/workflows/pages.yml`) that automatically builds and deploys the site when changes are pushed to the `master` or `main` branch.

To enable:
1. Go to your repository settings
2. Navigate to "Pages" in the left sidebar
3. Under "Source", select "GitHub Actions"
4. The workflow will automatically deploy on the next push

The site will be available at `https://<username>.github.io/coala/`

## Features

- ✅ Automatic markdown compilation
- ✅ Modern, responsive design
- ✅ Dark/light theme support
- ✅ Built-in search
- ✅ Code syntax highlighting
- ✅ Mermaid diagram support
- ✅ Fast page navigation
- ✅ SEO optimized

## Markdown Features

VitePress supports many markdown features out of the box:

- Code blocks with syntax highlighting
- Mermaid diagrams
- Custom containers (tip, warning, danger, etc.)
- Frontmatter for page metadata
- And much more!

See the [VitePress documentation](https://vitepress.dev/guide/markdown) for details.
