// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import remarkUnwrapImages from 'remark-unwrap-images';

// https://astro.build/config
export default defineConfig({
  site: 'https://exegesis.space',
  integrations: [mdx(), sitemap()],

  redirects: {
    '/': '/entry/sensor-contact',
  },

  markdown: {
    remarkPlugins: [remarkUnwrapImages]
  },

  vite: {
    plugins: [tailwindcss()],
  },
});
