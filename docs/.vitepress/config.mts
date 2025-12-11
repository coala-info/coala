import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  title: 'Coala',
  description: 'Convert any command-line tool into a Large Language Model (LLM) agent using MCP and CWL',
  base: '/coala/',
  
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/' },
      { text: 'Use Cases', link: '/use-cases/' },
      { text: 'GitHub', link: 'https://github.com/hubentu/coala' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Overview', link: '/guide/' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Quick Start', link: '/guide/quick-start' }
          ]
        },
        {
          text: 'Usage',
          items: [
            { text: 'MCP Server', link: '/guide/mcp-server' },
            { text: 'Function Call', link: '/guide/function-call' }
          ]
        }
      ],
      '/use-cases/': [
        {
          text: 'Use Cases',
          items: [
            { text: 'Overview', link: '/use-cases/' },
            { text: 'PDF Operations', link: '/use-cases/pdf-operations' },
            { text: 'TP53 Gene Analysis', link: '/use-cases/tp53-gene-analysis' },
            { text: 'RNA-Seq Analysis', link: '/use-cases/rnaseq-analysis' },
            { text: 'ATAC-Seq Analysis', link: '/use-cases/atacseq-analysis' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/hubentu/coala' }
    ],

    search: {
      provider: 'local'
    },

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024 Tool Agent'
    },

    editLink: {
      pattern: 'https://github.com/hubentu/coala/edit/master/docs/:path',
      text: 'Edit this page on GitHub'
    }
  },

  markdown: {
    lineNumbers: true
  },

  mermaid: {
    // Mermaid configuration
  }
}))

