import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const entry = defineCollection({
    // Load Markdown and MDX files in the `src/content/entry/` directory.
    loader: glob({ base: './src/content/entry', pattern: '**/*.{md,mdx}' }),
    // Type-check frontmatter using a schema
    schema: ({ image }) =>
        z.object({
            published: z.boolean(),
            entryNumber: z.number().int(),
            title: z.string(),
            showTitle: z.boolean().default(true),
            description: z.string(),
            heroImage: image().optional(),
            previousEntry: z.string().nullable(),
            nextEntry: z.string().nullable()
        }),
});

export const collections = { entry };
