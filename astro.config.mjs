// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import remarkUnwrapImages from 'remark-unwrap-images';

// https://astro.build/config
export default defineConfig({
  site: 'https://choccccy.github.io',
  // base: '/exegesis-site',
  integrations: [mdx(), sitemap()],
  markdown: {
    remarkPlugins: [remarkUnwrapImages]
  },

  vite: {
    plugins: [tailwindcss()],
  },
});
