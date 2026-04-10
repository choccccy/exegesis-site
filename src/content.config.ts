import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const entry = defineCollection({
    // Load Markdown and MDX files in the `src/content/entry/` directory.
    loader: glob({ 
        base: './src/content/entry', 
        pattern: '**/*.mdx',
        generateId: ({ entry }) => {
            // Extract the filename without extension from the path
            // e.g., "orbital-insertion/orbital-insertion.mdx" -> "orbital-insertion"
            const parts = entry.split('/');
            const filename = parts[parts.length - 1];  // Get last part (filename)
            return filename.replace(/\.mdx?$/, '');    // Remove .md or .mdx extension
        }
    }),
    // Type-check frontmatter using a schema
    schema: ({ image }) =>
        z.object({
            status: z.enum(['published', 'in-progress', 'draft']).default('draft'),
            entryNumber: z.number().int(),
            title: z.string(),
            showTitle: z.boolean().default(true),
            description: z.string(),
            heroImage: image(),
            previousEntry: z.string().nullable(),
            nextEntry: z.string().nullable(),
            NSFW: z.boolean().default(false)
        }),
});

export const collections = { entry };

// const codex = defineCollection({
// 	loader: glob({
// 		base: './src/content/codex',
// 		pattern: '**/*.mdx',
// 		generateId: ({ entry }) => {
// 			const parts = entry.split('/');
// 			const filename = parts[parts.length - 1];
// 			return filename.replace(/\.mdx?$/, '');
// 		},
// 	}),
// 	schema: z.object({
// 		published: z.boolean(),
// 		title: z.string(),
// 		type: z.enum([
// 			'character',
// 			'place',
// 			'vehicle',
// 			'object',
// 			'event',
// 			'group',
// 			'concept',
// 		]),
// 		summary: z.string(),
// 		tags: z.array(z.string()).default([]),
// 		relatedEntries: z.array(z.string()).default([]),
// 		relatedCodex: z.array(z.string()).default([]),

// 		// Character-ish
// 		species: z.string().optional(),
// 		affiliation: z.string().optional(),
// 		role: z.string().optional(),
// 		status: z.string().optional(),

// 		// Place / object
// 		location: z.string().optional(),
// 		scale: z.string().optional(),
// 		era: z.string().optional(),

// 		// Vehicle
// 		class: z.string().optional(),
// 		manufacturer: z.string().optional(),
// 		crew: z.string().optional(),
// 		driveType: z.string().optional(),

// 		// Event
// 		date: z.string().optional(),
// 	}),
// });

// export const collections = { entry, codex };
