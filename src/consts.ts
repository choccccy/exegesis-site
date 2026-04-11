// Place any global data in this file.
// You can import this data from anywhere in your site by using the `import` keyword.

export const SITE_TITLE = 'Exegesis';
export const SITE_DESCRIPTION = 'Some heavens wait for nothing...';

// External links
export const DISCORD_URL = 'https://discord.gg/CAHWY2wKWu';
export const VR_AVATARS_REPO = 'https://github.com/choccccy/exegesis_social_VR';

// Arc metadata: display name, accent color, and sort order
export interface ArcInfo {
    name: string;
    color: string;
    order: number;
}

export const ARCS: Record<string, ArcInfo> = {
    'intro': { name: 'Introduction', color: '#c0c0c0', order: 1 },
    'empyrean-beam': { name: "Nysa's Wake Gets Microwaved", color: '#c0c0c0', order: 2 },
    'amur-displacement': { name: "Amur Team's First Big Outing", color: '#c0c0c0', order: 3 },
    'misc': { name: 'Misc./Interstitial', color: '#c0c0c0', order: 4 },
    'prelude': { name: 'Prelude', color: '#c0c0c0', order: 5 },
    'evil': { name: 'Evil', color: '#c0c0c0', order: 6 },
};
