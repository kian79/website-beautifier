SYSTEM_PROMPT = """\
You are an expert UI/UX designer and frontend developer. Your job is to take the HTML structure and content of a webpage and return a completely redesigned, beautiful version.

Technology Stack:
- Use Tailwind CSS via CDN. Add this in the <head>:
  <script src="https://cdn.tailwindcss.com"></script>
- Use Tailwind utility classes for ALL styling. Do NOT write custom CSS except for minor animations.
- You may use Google Fonts via a <link> tag.
- You may use Heroicons or Font Awesome via CDN for icons if needed.

Design Rules:
- Return ONLY a single, complete, self-contained HTML file. No markdown, no explanation, no code fences.
- Start your response with <!DOCTYPE html> — nothing before it.
- Make the design modern, clean, and professional following these principles:
  - A cohesive color palette (2-3 primary colors + neutrals) using Tailwind's color system
  - Good typography hierarchy (clear headings, readable body text, proper line-height)
  - Generous whitespace and padding
  - Subtle shadows (shadow-sm, shadow-md), rounded corners (rounded-lg, rounded-xl), and hover effects
  - Fully responsive design using Tailwind's responsive prefixes (sm:, md:, lg:)
  - Use flexbox and grid utilities for layout (flex, grid, gap-*, etc.)

Component Style References (use these patterns):
- Hero sections: Full-width with gradient background (bg-gradient-to-r), large heading, subtitle, and CTA buttons
- Navigation: Sticky top navbar with flex layout, logo left, links right, mobile hamburger menu
- Feature grids: 3-column grid (grid-cols-1 md:grid-cols-3) with icon + heading + description cards
- Testimonials: Cards with quote, avatar (w-12 h-12 rounded-full), name and role
- Pricing: Side-by-side cards with highlighted "popular" plan using ring-2 and scale-105
- CTA sections: Centered text with gradient or colored background and prominent button
- Footer: Multi-column grid with links, dark background (bg-gray-900 text-gray-400)

Content Rules:
- Preserve ALL original text content exactly as-is. Do not add, remove, or change any text.
- Preserve all images — keep the original src URLs. Style them with Tailwind (rounded-lg, shadow-md, object-cover).
- Profile/avatar photos must be kept small (w-32 h-32 or w-40 h-40 max) with rounded-full for portraits.
- All images should have max-width constraints (max-w-xs, max-w-sm, max-w-md). Never let an image stretch full width.
- Preserve all links with their original href values.
- Preserve the semantic structure (nav, header, main, footer, sections).

Layout Rules:
- If the original page has a navigation menu, make it a modern sticky responsive navbar.
- If there's a hero section, make it visually impactful with a gradient background.
- Use container mx-auto px-4 for consistent content width.
- Add a subtle footer crediting "Redesigned by Beautify AI" at the very bottom.

Important:
- The HTML you receive has been cleaned (scripts/styles removed). You must infer the page layout from the semantic tags, class names, and content structure.
- Look at class names and IDs for hints about what each section is (e.g., "hero", "features", "pricing", "testimonials", "cta").
- If images have broken src URLs or alt text only, use the alt text as a label and show a styled placeholder with bg-gray-200.
- Create a FULL, rich page — not a skeleton. Every section in the original should appear in your redesign with proper styling.\
"""


PALETTE_DESCRIPTIONS = {
    "Ocean Blue": "shades of blue, navy, and white as the primary colors",
    "Forest Green": "shades of green, emerald, and cream as the primary colors",
    "Sunset Warm": "warm oranges, corals, and soft yellows as the primary colors",
    "Purple Haze": "purples, lavenders, and soft pinks as the primary colors",
    "Monochrome": "black, white, and shades of gray as the primary colors",
    "Corporate Blue": "professional blues, slate grays, and white as the primary colors",
}

DESIGN_STYLE_DESCRIPTIONS = {
    "Minimal": (
        "Use a minimalist design approach: lots of whitespace, clean lines, "
        "limited color usage, simple typography, no visual clutter. "
        "Think Apple/Stripe style — elegant simplicity."
    ),
    "Bold & Vibrant": (
        "Use a bold, vibrant design: large colorful gradients, oversized typography, "
        "strong contrast, eye-catching CTAs, energetic feel. "
        "Think startup landing pages with punchy visuals."
    ),
    "Elegant": (
        "Use an elegant, sophisticated design: serif fonts for headings, "
        "muted tones, refined spacing, subtle gold/cream accents, "
        "thin borders. Think luxury brand or editorial magazine."
    ),
    "Glassmorphism": (
        "Use glassmorphism design: frosted glass cards with backdrop-blur, "
        "semi-transparent backgrounds (bg-white/10 backdrop-blur-lg), "
        "subtle borders (border-white/20), gradient backgrounds behind glass panels."
    ),
    "Dark Mode": (
        "Use a dark mode design: dark backgrounds (bg-gray-950, bg-slate-900), "
        "light text (text-gray-100), accent colors that pop against dark, "
        "subtle glow effects, dark cards with light borders."
    ),
    "Retro / Vintage": (
        "Use a retro/vintage design: warm earthy tones (amber, brown, cream), "
        "vintage-inspired typography, textured backgrounds, "
        "rounded shapes, nostalgic feel with modern layout techniques."
    ),
}

FONT_PAIRING_DESCRIPTIONS = {
    "Modern Sans": (
        "Use Google Font 'Inter' for all text. Clean, modern, and highly readable. "
        "Add: <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' rel='stylesheet'>"
    ),
    "Editorial Serif": (
        "Use Google Font 'Playfair Display' for headings and 'Source Sans 3' for body. Elegant editorial feel. "
        "Add: <link href='https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Source+Sans+3:wght@400;500;600&display=swap' rel='stylesheet'>"
    ),
    "Tech Geometric": (
        "Use Google Font 'Space Grotesk' for headings and 'DM Sans' for body. Techy, geometric feel. "
        "Add: <link href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;600&display=swap' rel='stylesheet'>"
    ),
    "Friendly Rounded": (
        "Use Google Font 'Nunito' for all text. Friendly, rounded, approachable feel. "
        "Add: <link href='https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap' rel='stylesheet'>"
    ),
    "Classic Slab": (
        "Use Google Font 'Roboto Slab' for headings and 'Roboto' for body. Classic, authoritative feel. "
        "Add: <link href='https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;500;600;700&family=Roboto:wght@400;500;600&display=swap' rel='stylesheet'>"
    ),
}

VISUAL_EFFECTS_DESCRIPTIONS = {
    "Subtle Animations": (
        "Add subtle CSS animations: fade-in on scroll sections using @keyframes fadeInUp, "
        "smooth hover transitions on cards (hover:-translate-y-1 hover:shadow-xl transition-all duration-300), "
        "gentle scale on buttons (hover:scale-105). Keep it professional, not flashy."
    ),
    "Gradient Accents": (
        "Use gradient accents throughout: gradient text on main headings (bg-gradient-to-r bg-clip-text text-transparent), "
        "gradient borders on cards, gradient CTA buttons, "
        "gradient dividers between sections. Make gradients cohesive with the color palette."
    ),
    "Card Depth": (
        "Emphasize depth and layering: elevated cards with strong shadows (shadow-xl), "
        "overlapping sections, cards with hover lift effects (hover:-translate-y-2 hover:shadow-2xl), "
        "stacked/offset elements for visual interest."
    ),
    "Smooth Transitions": (
        "Add smooth transitions everywhere: all interactive elements get transition-all duration-300, "
        "color transitions on links, background transitions on buttons, "
        "transform transitions on cards. Make the page feel alive and responsive to interaction."
    ),
}


def build_user_prompt(
    cleaned_html: str,
    page_title: str,
    original_url: str,
    color_palette: str | None = None,
    design_style: str | None = None,
    font_pairing: str | None = None,
    visual_effects: str | None = None,
    instructions: str | None = None,
) -> str:
    parts = [
        f'Here is the HTML of a webpage titled "{page_title}" from {original_url}.\n'
        f"Please redesign it into a beautiful, modern page using Tailwind CSS utility classes. "
        f"Make sure to include ALL sections and content from the original — do not skip anything.",
    ]

    if color_palette and color_palette in PALETTE_DESCRIPTIONS:
        parts.append(
            f"COLOR PALETTE: {color_palette} — use {PALETTE_DESCRIPTIONS[color_palette]}."
        )

    if design_style and design_style in DESIGN_STYLE_DESCRIPTIONS:
        parts.append(
            f"DESIGN STYLE: {DESIGN_STYLE_DESCRIPTIONS[design_style]}"
        )

    if font_pairing and font_pairing in FONT_PAIRING_DESCRIPTIONS:
        parts.append(
            f"FONT PAIRING: {FONT_PAIRING_DESCRIPTIONS[font_pairing]}"
        )

    if visual_effects and visual_effects in VISUAL_EFFECTS_DESCRIPTIONS:
        parts.append(
            f"VISUAL EFFECTS: {VISUAL_EFFECTS_DESCRIPTIONS[visual_effects]}"
        )

    if instructions and instructions.strip():
        parts.append(f"ADDITIONAL INSTRUCTIONS: {instructions.strip()}")

    parts.append(
        f"---HTML START---\n"
        f"{cleaned_html}\n"
        f"---HTML END---"
    )

    return "\n\n".join(parts)
